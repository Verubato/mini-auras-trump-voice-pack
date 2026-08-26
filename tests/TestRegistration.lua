-- The addon is one call into MiniAuras, so these stub its API and check what it was handed,
-- including the case where MiniAuras is not there yet when the file runs.

local fw = require("TestFramework")
local harness = require("AddonHarness")
local WowMock = require("WowMock")

local ADDON = "MiniAurasVoicePackTrump"
local FILE = "src/MiniAurasVoicePackTrump.lua"

---A stand-in for MiniAuras that records every pack handed to it.
---@param registered table
---@return table
local function NewApi(registered)
	return {
		v1 = {
			RegisterVoicePack = function(_, pack)
				registered[#registered + 1] = pack

				return true
			end,
		},
	}
end

---@param api table? what MiniAuras has published before the addon loads, if anything
local function LoadWith(api)
	WowMock.Install()

	_G.MiniAurasApi = api

	harness.LoadFiles(ADDON, { FILE }, {})
end

---@return table registered
local function Load()
	local registered = {}

	LoadWith(NewApi(registered))

	return registered
end

fw.describe(ADDON .. " - voice pack registration", function()
	fw.it("hands the pack over when the API is already there", function()
		local registered = Load()

		fw.eq(#registered, 1, "packs registered")
		fw.eq(registered[1].Name, "Trump", "pack name")
	end)

	fw.it("points the pack at its own folder of clips", function()
		local registered = Load()

		fw.eq(
			registered[1].Path,
			"Interface\\AddOns\\MiniAurasVoicePackTrump\\Sounds\\Trump\\",
			"pack path"
		)
	end)

	fw.it("names no locales, so the pack is offered on every client", function()
		local registered = Load()

		-- MiniAuras hides a pack that names locales from the clients it left out.
		for i = 1, #registered do
			fw.no_key(registered[i], "Locales", "locales for " .. registered[i].Name)
		end
	end)

	fw.it("waits for a MiniAuras that loads after it", function()
		local registered = {}

		LoadWith(nil)

		fw.eq(#registered, 0, "nothing to register against")

		_G.MiniAurasApi = NewApi(registered)
		WowMock.FireEvent("ADDON_LOADED", "MiniAuras")

		fw.eq(#registered, 1, "pack registered once the API arrived")
	end)

	fw.it("gives up once MiniAuras has loaded, however its API turned out", function()
		local registered = {}

		LoadWith(nil)

		WowMock.FireEvent("ADDON_LOADED", "MiniAuras")

		-- Nothing can publish the API after MiniAuras' own load, so a later one is not ours.
		_G.MiniAurasApi = NewApi(registered)
		WowMock.FireEvent("ADDON_LOADED", "MiniAuras")

		fw.eq(#registered, 0, "the waiter stopped at the first MiniAuras load")
	end)

	fw.it("keeps waiting while some other addon loads", function()
		local registered = {}

		LoadWith(nil)

		_G.MiniAurasApi = NewApi(registered)
		WowMock.FireEvent("ADDON_LOADED", "SomethingElse")

		fw.eq(#registered, 0, "another addon's load is not the signal")

		WowMock.FireEvent("ADDON_LOADED", "MiniAuras")

		fw.eq(#registered, 1, "MiniAuras' own load is")
	end)

	fw.it("loads cleanly against a MiniAuras too old to know about voice packs", function()
		-- The API global exists from 5.0.0, but RegisterVoicePack only from 5.1.0, so calling
		-- it unguarded is what an older MiniAuras would break on.
		fw.no_error(function()
			LoadWith({ v1 = {} })
		end, "loading against an API without RegisterVoicePack")
	end)
end)
