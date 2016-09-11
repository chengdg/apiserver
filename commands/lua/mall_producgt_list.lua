local JSON = require("cjson")
local uri_args = ngx.req.get_uri_args()
-- for k, v in pairs(uri_args) do
--    if type(v) == "table" then
--        ngx.say(k, " : ", table.concat(v, ", "), "<br/>")
--    else
--        ngx.say(k, ": ", v, "<br/>")
--    end
-- end

-- TODO connection pool by bert
local redis = require "resty.redis"
local red = redis:new()
red:set_timeout(1000)
local ok, err = red:connect("127.0.0.1", 6379)
-- local ok, err = red:set("dog", "{x:y}")
-- if not ok then
--    ngx.say("failed to set dog: ", err)
--    return
-- end

local result = red:get('dog')
ngx.header.content_type = 'application/json'
-- local x = JSON.decode(result)
ngx.say(result)