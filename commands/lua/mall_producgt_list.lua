---location /apiserver/ {
--                 rewrite ^/apiserver/(.*) /$1 break;
--                 proxy_pass http://127.0.0.1:8001;
--         }

-- location /default/ {
--         rewrite ^/default/(.*) /$1 break;
--         proxy_set_header Host $host;
--         proxy_set_header X-Real-IP $remote_addr;
--         include uwsgi_params;
--         #uwsgi_pass 127.0.0.1:8001;
--         content_by_lua_file /usr/local/etc/openresty/lua/mall_proudct_list.lua;
-- #      proxy_pass http://127.0.0.1:8001;
-- }
---

local JSON = require("cjson")
local uri_args = ngx.req.get_uri_args()

local x =  "/apiserver"..ngx.var.uri
-- ngx.log(ngx.ERR, x)
-- ngx.say(ngx.req.get_method())
local method = ngx.req.get_method()

if method == "GET" then
    method = ngx.HTTP_GET
else
    method = ngx.HTTP_POST
end

if string.find(x,"/mall/products") and ngx.req.get_method() == "GET" then
    local woid = uri_args.woid
    local category = uri_args.category_id
    local key = "w_"..woid.."_c_"..category
    local redis = require "resty.redis_iresty"
    local red = redis:new()
    local result = red:get(key)
    if result then
        ngx.header.content_type = 'application/json'
        ngx.say(result)
    else
        local res = ngx.location.capture(x, {
             method=ngx.HTTP_GET,
            args=ngx.req.get_uri_args()
        })
        ngx.req.set_header("Accept", "application/json");
    	ngx.say(res.body)
    end
elseif string.find(x,"/mall/global_navbar") and ngx.req.get_method() == "GET" then
    local woid = uri_args.woid
    local key = "w_"..woid.."_g"
    local redis = require "resty.redis_iresty"
    local red = redis:new()
    local result = red:get(key)
    if result then
        ngx.header.content_type = 'application/json'
        ngx.say(result)
    else
        local res = ngx.location.capture(x, {
             method=ngx.HTTP_GET,
            args=ngx.req.get_uri_args()
        })
        ngx.req.set_header("Content-Type", "application/json;charset=utf8");
        ngx.req.set_header("Accept", "application/json");
        ngx.say(res.body)
    end
else
    local res = ""
    if ngx.req.get_method() == "GET" then
        res = ngx.location.capture(x, {
            method=ngx.HTTP_GET,
            args=ngx.req.get_uri_args()
        })
    else
        res = ngx.location.capture(x, {
            method=ngx.HTTP_POST,
            args=ngx.req.get_post_args()
        })
    end
    ngx.req.set_header("Content-Type", "application/json;charset=utf8");
    ngx.req.set_header("Accept", "application/json");
    ngx.say(res.body)
end