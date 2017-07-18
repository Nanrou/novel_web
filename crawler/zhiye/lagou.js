var page = require('webpage').create(),
    system = require('system'),
    address;
var fs = require('fs');
var path = './lagou_cookies.txt';
var content = ''
    
    
address = system.args[1];
 
//init and settings
page.settings.resourceTimeout = 30000 ;
page.settings.XSSAuditingEnabled = true ;
page.settings.userAgent = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36';
page.customHeaders = {
    "Connection" : "keep-alive",
    "Cache-Control" : "max-age=0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.8,en;q=0.6",
};
page.open(address);
//加载页面完毕运行
page.onLoadFinished = function(status) {
  var cookies = page.cookies;
  for (var i in cookies){
    content = content + cookies[i].name + '=' + cookies[i].value + '\n';  
  }
  fs.write(path, content, 'w');
  phantom.exit();
};