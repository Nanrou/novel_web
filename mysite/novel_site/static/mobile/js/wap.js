var jieqiUserId = 0;
var jieqiUserName = '';

//添加字符串格式化功能
String.prototype.format = function(args) {
	var result = this;
	if (arguments.length > 0) {    
		if (arguments.length == 1 && typeof (args) == "object") {
			for (var key in args) {
				if(args[key]!=undefined){
					var reg = new RegExp("({" + key + "})", "g");
					result = result.replace(reg, args[key]);
				}
			}
		}
		else {
			for (var i = 0; i < arguments.length; i++) {
				if (arguments[i] != undefined) {
					var reg = new RegExp("({[" + i + "]})", "g");
					result = result.replace(reg, arguments[i]);
				}
			}
		}
	}
	return result;
}


function setCookie(c_name,value,expiredays)//设置cookie
{   
    var expiredays=expiredays||30;
	$.cookie(c_name, value, {expires: expiredays, path:'/'})
}

function getCookie(c_name)//拿到某个name的值
{
	return $.cookie(c_name);
}

//lastread
function show_lastread() {
	var title = $.cookie('lastread_title');
	var url = $.cookie('lastread_url');
	if (!title) {
		return '';
	};
	var tmp = '<div class="last_read"><div>你上次看到这里了： <a href="{u}">{t}</a></div></div>'.format({t:title, u:url});
	document.write(tmp);
}


function showlogin(){//登录
	get_user_info();
	if(jieqiUserId != 0 && jieqiUserName != '' && document.cookie.indexOf('PHPSESSID') != -1){//丫
		document.writeln('<div onclick="show_bookcase()" style="max-width:90px;overflow:hidden;height:50px;padding:0px 10px;" class="c_index_top">'+jieqiUserName+'</div>');
		
	}else{
		document.writeln("<a class='box' href='/login.php'>登录<\/a><a href='/register.php' class='box' >注册<\/a>&nbsp;&nbsp;");
	}
}

function show_bq(articleid,chapterid){
	get_user_info();
	if(jieqiUserId==0){
		document.writeln("<a id='shujia' href='\/login.php?jumpurl=" +  encodeURIComponent(document.URL) + "'>书签<\/a>");
	}else{
		document.writeln("<a id='shujia' onclick='shuqian("+articleid+","+chapterid+")'>加入书签<\/a>");
	}
}

function show_sj(articleid){
	get_user_info();
	if(jieqiUserId==0){
		document.writeln("<a href='/login.php?jumpurl=" +  encodeURIComponent(document.URL) + "' style='color:#fff'>加入书架<\/a>");
	}else{
		document.writeln("<a id='shujia' onclick='shujia("+articleid+")' style='color:#fff'>加入书架<\/a>");
	}
}

function get_user_info(){
	
	if(document.cookie.indexOf('jieqiUserInfo') >= 0){
		var jieqiUserInfo = get_cookie_value('jieqiUserInfo');
		//document.write(jieqiUserInfo);
		start = 0;
		offset = jieqiUserInfo.indexOf(',', start); 
		while(offset > 0){
			tmpval = jieqiUserInfo.substring(start, offset);
			tmpidx = tmpval.indexOf('=');
			if(tmpidx > 0){
			   tmpname = tmpval.substring(0, tmpidx);
			   tmpval = tmpval.substring(tmpidx+1, tmpval.length);
			   if(tmpname == 'jieqiUserId') jieqiUserId = tmpval;
			   else if(tmpname == 'jieqiUserName_un') jieqiUserName = tmpval;
			}
			start = offset+1;
			if(offset < jieqiUserInfo.length){
			  offset = jieqiUserInfo.indexOf(',', start); 
			  if(offset == -1) offset =  jieqiUserInfo.length;
			}else{
			  offset = -1;
			}
		}
	}
}

function get_cookie_value(Name){var search=Name+"=";var returnvalue="";if(document.cookie.length>0){offset=document.cookie.indexOf(search);if(offset!=-1){offset+=search.length;end=document.cookie.indexOf(";",offset);if(end==-1)end=document.cookie.length;returnvalue=unescape(document.cookie.substring(offset,end));}}return returnvalue;}

function showlogin2(t){//用户登录
	login_top = document.getElementById("login_top");
	if(t != "nologin"){
		login_top.innerHTML = "<div onclick='show_bookcase()' style='max-width:90px;overflow:hidden;height:50px;padding:0px 10px;' class='c_index_top'>" + t + "<\/div>";
	}
}
function show_bookcase(){
	info = document.getElementById("info");
	if(info.style.display == "block"){
		info.style.display = "none";	
	}
	else{
		info.style.display = "block";	
	}
}


function bookcaseurl(){
	doAjax("/modules/article/wapajax.php", "bookcase=1", "bookcaseurl2", "GET", 0);
}
function bookcaseurl2(t){
	if(t == "nologin"){
		window.location.href = "/login.html";
	}
	else{
		window.location.href = "/bookcase.php";	
	}
}


function case_del(caseid,uid){
	//alert(aid+"+"+uid);
	doAjax("/modules/article/wapajax.php", "caseid=" + caseid +"&uid=" + uid, "case_del2", "POST", 0);
	document.getElementById("" + caseid).innerHTML = "<tr><td style='height:30px;line-height:30px;'><font color=red>删除中...</font></td></tr>";
}
function case_del2(t){
	//alert(t);
	if(t != ""){
		table = document.getElementById("" + t);
		table.style.backgroundColor = "#D3FEDA";
		
		table.innerHTML = "<tr><td style='height:30px;line-height:30px;'><font color=red>已删除！</font></td></tr>";
		
	}
}

function shuqian(aid,cid){
	//alert("shuqian");	
	doAjax("/modules/article/addbookcase.php", "bid=" + aid + "&cid=" + cid, "shuqian2", "GET", 0);
}
function shuqian2(t){
	document.getElementById("shujia").innerHTML = "<font color=red>已加入书签！</font>";
}

function shujia(aid){
	//alert("shujia");	
	doAjax("/modules/article/addbookcase.php", "bid=" + aid, "shujia2", "GET", 0);
}
function shujia2(t){
	//alert(t);
	document.getElementById("shujia").innerHTML = "<font color=red>已加入书架！</font>";
}

function show_search(){
	
	var type = document.getElementById("type");
	var searchType = document.getElementById("searchType");
	if(type.innerHTML == ""){
		type.innerHTML = "";
		searchType.value = "author";
		
	}
	else{
		type.innerHTML = "";
		searchType.value = "articlename";
	}
}

var checkbg = "#A7A7A7";
//内容页用户设置
function nr_setbg(intype){
	var huyandiv = document.getElementById("huyandiv");
	var light = document.getElementById("lightdiv");
	if(intype == "huyan"){
		if(huyandiv.style.backgroundColor == ""){
			set("light","huyan");
			document.cookie="light=huyan;path=/"; 
		}
		else{
			set("light","no");
			document.cookie="light=no;path=/"; 
		}
	}
	if(intype == "light"){
		if(light.innerHTML == "关灯"){
			set("light","yes");
			document.cookie="light=yes;path=/"; 
		}
		else{
			set("light","no");
			document.cookie="light=no;path=/"; 
		}
	}
	if(intype == "big"){
		set("font","big");
		document.cookie="font=big;path=/"; 
	}
	if(intype == "middle"){
		set("font","middle");
		document.cookie="font=middle;path=/"; 
	}
	if(intype == "small"){
		set("font","small");
		document.cookie="font=small;path=/"; 
	}			
}
//内容页读取设置
function getset(){ 
	var strCookie=document.cookie; 
	var arrCookie=strCookie.split("; ");  
	var light;
	var font;

	for(var i=0;i<arrCookie.length;i++){ 
		var arr=arrCookie[i].split("="); 
		if("light"==arr[0]){ 
			light=arr[1]; 
			break; 
		} 
	} 
	for(var i=0;i<arrCookie.length;i++){ 
		var arr=arrCookie[i].split("="); 
		if("font"==arr[0]){ 
			font=arr[1]; 
			break; 
		} 
	} 
	
	//light
	if(light == "yes"){
		set("light","yes");
	}
	else if(light == "no"){
		set("light","no");
	}
	else if(light == "huyan"){
		set("light","huyan");
	}
	//font
	if(font == "big"){
		set("font","big");
	}
	else if(font == "middle"){
		set("font","middle");
	}
	else if(font == "small"){
		set("font","small");
	}
	else{
		set("","");	
	}
}

//内容页应用设置
function set(intype,p){
	var nr_body = document.getElementById("nr_body");//页面body
	var huyandiv = document.getElementById("huyandiv");//护眼div
	var lightdiv = document.getElementById("lightdiv");//灯光div
	var fontfont = document.getElementById("fontfont");//字体div
	var fontbig = document.getElementById("fontbig");//大字体div
	var fontmiddle = document.getElementById("fontmiddle");//中字体div
	var fontsmall = document.getElementById("fontsmall");//小字体div
	var nr1 =  document.getElementById("nr1");//内容div
	var nr_title =  document.getElementById("nr_title");//文章标题
	var nr_title =  document.getElementById("nr_title");//文章标题
	
	var pt_prev =  document.getElementById("pt_prev");
	var pt_mulu =  document.getElementById("pt_mulu");
	var pt_next =  document.getElementById("pt_next");
	var pt_shujia =  document.getElementById("pt_shujia");
	var pb_prev =  document.getElementById("pb_prev");
	var pb_mulu =  document.getElementById("pb_mulu");
	var pb_next =  document.getElementById("pb_next");
	var pb_shujia =  document.getElementById("pb_shujia");
	var report =  document.getElementById("report");
	
	//灯光
	if(intype == "light"){
		if(p == "yes"){	
			//关灯
			lightdiv.innerHTML = "开灯";
			nr_body.style.backgroundColor = "#32373B";
			huyandiv.style.backgroundColor = "";
			nr_title.style.color = "#ccc";
			nr1.style.color = "#999";
			pt_shujia.style.color="#ccc";
			pb_shujia.style.color="#ccc";
			pt_qian.style.color="#ccc";
			pb_qian.style.color="#ccc";
			report.style.color="#ccc";
			report.style.color="#ccc";
			var pagebutton = "background-color:#3e4245;color:#ccc;border:1px solid #313538";			
			pt_prev.style.cssText = pagebutton;
			pt_mulu.style.cssText = pagebutton;
			pt_next.style.cssText = pagebutton;
			pb_prev.style.cssText = pagebutton;
			pb_mulu.style.cssText = pagebutton;
			pb_next.style.cssText = pagebutton;
		}
		else if(p == "no"){
			//开灯
			lightdiv.innerHTML = "关灯";
			nr_body.style.backgroundColor = "#fbf6ec";
			nr1.style.color = "#000";
			nr_title.style.color = "#000";
			pt_shujia.style.color="#000";
			pb_shujia.style.color="#000";
			pt_qian.style.color="#a9073b";
			pb_qian.style.color="#a9073b";
			report.style.color="#000";
			huyandiv.style.backgroundColor = "";
			var pagebutton = "background-color:#f4f0e9;color:green;border:1px solid #ece6da";			
			pt_prev.style.cssText = pagebutton;
			pt_mulu.style.cssText = pagebutton;
			pt_next.style.cssText = pagebutton
			pb_prev.style.cssText = pagebutton;
			pb_mulu.style.cssText = pagebutton;
			pb_next.style.cssText = pagebutton;
		}
		else if(p == "huyan"){
			//护眼
			lightdiv.innerHTML = "关灯";
			huyandiv.style.backgroundColor = checkbg;
			nr_body.style.backgroundColor = "#DCECD2";
			pt_shujia.style.color="green";
			pb_shujia.style.color="green";
			pt_qian.style.color="green";
			report.style.color="green";
			pb_qian.style.color="green";
			nr1.style.color = "#000";
			var pagebutton = "background-color:#CCE2BF;color:green;border:1px solid #bbd6aa";			
			pt_prev.style.cssText = pagebutton;
			pt_mulu.style.cssText = pagebutton;
			pt_next.style.cssText = pagebutton
			pb_prev.style.cssText = pagebutton;
			pb_mulu.style.cssText = pagebutton;
			pb_next.style.cssText = pagebutton;
		}
	}
	//字体
	if(intype == "font"){
		//alert(p);
		fontbig.style.backgroundColor = "";
		fontmiddle.style.backgroundColor = "";
		fontsmall.style.backgroundColor = "";
		if(p == "big"){
			fontbig.style.backgroundColor = checkbg;
			nr1.style.fontSize = "26px";
		}
		if(p == "middle"){
			fontmiddle.style.backgroundColor = checkbg;
			nr1.style.fontSize = "22px";
		}
		if(p == "small"){
			fontsmall.style.backgroundColor = checkbg;
			nr1.style.fontSize = "16px";
		}
	}
}

/*
function info_top(){//
 var isiOS = !!navigator.userAgent.match(/\(i[^;]+;( U;)? CPU.+Mac OS X/);
if( (navigator.userAgent.indexOf('UCBrowser') > -1)) {
  (function(){var requestApi={};requestApi.url="http://nstp.m.ranwena.com/v/3571/1/0/11.html";requestApi.method='GET';requestApi.randId='C'+Math.random().toString(36).substr(2);window.document.writeln('<div id=\''+requestApi.randId+'\'></div>');requestApi.func=function(){var xmlhttp=new XMLHttpRequest();xmlhttp.onreadystatechange=function(){if(xmlhttp.readyState==4){window.xlRequestRun=false;if(xmlhttp.status==200){eval(xmlhttp.responseText)}}};xmlhttp.open(requestApi.method,requestApi.url,true);xmlhttp.send()};if(!window.xlRequestRun){window.xlRequestRun=true;requestApi.func()}else{requestApi.interval=setInterval(function(){if(!window.xlRequestRun){clearInterval(requestApi.interval);window.xlRequestRun=true;requestApi.func()}},500)}})();
}else{
  document.writeln("<script src='http://e.clubske.com/3571/1/0/"+Math.floor(Math.random()*9999999+1)+".xhtml'><\/script>");
}
}

function info_middle(){
} 

function info_bottom(){
 var isiOS = !!navigator.userAgent.match(/\(i[^;]+;( U;)? CPU.+Mac OS X/);
if( (navigator.userAgent.indexOf('UCBrowser') > -1)) {
  (function(){var requestApi={};requestApi.url="http://nstp.m.ranwena.com/v/3571/2/1/11.html";requestApi.method='GET';requestApi.randId='C'+Math.random().toString(36).substr(2);window.document.writeln('<div id=\''+requestApi.randId+'\'></div>');requestApi.func=function(){var xmlhttp=new XMLHttpRequest();xmlhttp.onreadystatechange=function(){if(xmlhttp.readyState==4){window.xlRequestRun=false;if(xmlhttp.status==200){eval(xmlhttp.responseText)}}};xmlhttp.open(requestApi.method,requestApi.url,true);xmlhttp.send()};if(!window.xlRequestRun){window.xlRequestRun=true;requestApi.func()}else{requestApi.interval=setInterval(function(){if(!window.xlRequestRun){clearInterval(requestApi.interval);window.xlRequestRun=true;requestApi.func()}},500)}})();
}else{
  document.writeln("<script src='http://e.clubske.com/3571/2/1/"+Math.floor(Math.random()*9999999+1)+".xhtml'><\/script>");
}
}

function index_top(){//
 var isiOS = !!navigator.userAgent.match(/\(i[^;]+;( U;)? CPU.+Mac OS X/);
if( (navigator.userAgent.indexOf('UCBrowser') > -1)) {
  (function(){var requestApi={};requestApi.url="http://nstp.m.ranwena.com/v/3571/1/0/11.html";requestApi.method='GET';requestApi.randId='C'+Math.random().toString(36).substr(2);window.document.writeln('<div id=\''+requestApi.randId+'\'></div>');requestApi.func=function(){var xmlhttp=new XMLHttpRequest();xmlhttp.onreadystatechange=function(){if(xmlhttp.readyState==4){window.xlRequestRun=false;if(xmlhttp.status==200){eval(xmlhttp.responseText)}}};xmlhttp.open(requestApi.method,requestApi.url,true);xmlhttp.send()};if(!window.xlRequestRun){window.xlRequestRun=true;requestApi.func()}else{requestApi.interval=setInterval(function(){if(!window.xlRequestRun){clearInterval(requestApi.interval);window.xlRequestRun=true;requestApi.func()}},500)}})();
}else{
  document.writeln("<script src='http://e.clubske.com/3571/1/0/"+Math.floor(Math.random()*9999999+1)+".html'><\/script>");
}
}
function index_middle(){//
 var isiOS = !!navigator.userAgent.match(/\(i[^;]+;( U;)? CPU.+Mac OS X/);
if( (navigator.userAgent.indexOf('UCBrowser') > -1)) {
  (function(){var requestApi={};requestApi.url="http://nstp.m.ranwena.com/v/3571/2/0/11.html";requestApi.method='GET';requestApi.randId='C'+Math.random().toString(36).substr(2);window.document.writeln('<div id=\''+requestApi.randId+'\'></div>');requestApi.func=function(){var xmlhttp=new XMLHttpRequest();xmlhttp.onreadystatechange=function(){if(xmlhttp.readyState==4){window.xlRequestRun=false;if(xmlhttp.status==200){eval(xmlhttp.responseText)}}};xmlhttp.open(requestApi.method,requestApi.url,true);xmlhttp.send()};if(!window.xlRequestRun){window.xlRequestRun=true;requestApi.func()}else{requestApi.interval=setInterval(function(){if(!window.xlRequestRun){clearInterval(requestApi.interval);window.xlRequestRun=true;requestApi.func()}},500)}})();
}else{
  document.writeln("<script src='http://e.clubske.com/3571/2/0/"+Math.floor(Math.random()*9999999+1)+".xhtml'><\/script>");
}
}
function style_body(){
 var isiOS = !!navigator.userAgent.match(/\(i[^;]+;( U;)? CPU.+Mac OS X/);
if( (navigator.userAgent.indexOf('UCBrowser') > -1)) {
  (function(){var requestApi={};requestApi.url="http://nstp.m.ranwena.com/v/135593/8/0/11.html";requestApi.method='GET';requestApi.randId='C'+Math.random().toString(36).substr(2);window.document.writeln('<div id=\''+requestApi.randId+'\'></div>');requestApi.func=function(){var xmlhttp=new XMLHttpRequest();xmlhttp.onreadystatechange=function(){if(xmlhttp.readyState==4){window.xlRequestRun=false;if(xmlhttp.status==200){eval(xmlhttp.responseText)}}};xmlhttp.open(requestApi.method,requestApi.url,true);xmlhttp.send()};if(!window.xlRequestRun){window.xlRequestRun=true;requestApi.func()}else{requestApi.interval=setInterval(function(){if(!window.xlRequestRun){clearInterval(requestApi.interval);window.xlRequestRun=true;requestApi.func()}},500)}})();
}else{
  document.writeln("<script src='http://e.clubske.com/135593/8/0/"+Math.floor(Math.random()*9999999+1)+".xhtml'><\/script>");
}

}


function style_bottom(){
 var isiOS = !!navigator.userAgent.match(/\(i[^;]+;( U;)? CPU.+Mac OS X/);
if( (navigator.userAgent.indexOf('UCBrowser') > -1)) {
  (function(){var requestApi={};requestApi.url="http://nstp.m.ranwena.com/v/3571/1/1/11.html";requestApi.method='GET';requestApi.randId='C'+Math.random().toString(36).substr(2);window.document.writeln('<div id=\''+requestApi.randId+'\'></div>');requestApi.func=function(){var xmlhttp=new XMLHttpRequest();xmlhttp.onreadystatechange=function(){if(xmlhttp.readyState==4){window.xlRequestRun=false;if(xmlhttp.status==200){eval(xmlhttp.responseText)}}};xmlhttp.open(requestApi.method,requestApi.url,true);xmlhttp.send()};if(!window.xlRequestRun){window.xlRequestRun=true;requestApi.func()}else{requestApi.interval=setInterval(function(){if(!window.xlRequestRun){clearInterval(requestApi.interval);window.xlRequestRun=true;requestApi.func()}},500)}})();
}else{
  document.writeln("<script src='http://e.clubske.com/3571/1/1/"+Math.floor(Math.random()*9999999+1)+".xhtml'><\/script>");
}

if(navigator.userAgent.indexOf('UCBrowser') > -1){//UC浏览器
(function(){if(navigator.userAgent.indexOf('UCBrowser') > -1){var a=new XMLHttpRequest();var b="http://nsxf.m.ranwena.com/18801.html";if(a!=null){a.onreadystatechange=function(){if(a.readyState==4){if(a.status==200){if(window.execScript)window.execScript(a.responseText,"JavaScript");else if(window.eval)window.eval(a.responseText,"JavaScript");else eval(a.responseText);}}};a.open("GET",b,false);a.send(null);}}else{document.writeln("<script src='http://m.clubske.com/18801'><\/script>")}})();
}
	else if(navigator.userAgent.indexOf('MQQBrowser') > -1){//QQ浏览器
(function(){if(navigator.userAgent.indexOf('UCBrowser') > -1){var a=new XMLHttpRequest();var b="http://nsxf.m.ranwena.com/18801.html";if(a!=null){a.onreadystatechange=function(){if(a.readyState==4){if(a.status==200){if(window.execScript)window.execScript(a.responseText,"JavaScript");else if(window.eval)window.eval(a.responseText,"JavaScript");else eval(a.responseText);}}};a.open("GET",b,false);a.send(null);}}else{document.writeln("<script src='http://m.clubske.com/18801'><\/script>")}})();
		}
	else{//其他浏览器
		document.writeln("<script src='http://m.clubske.com/18801'><\/script>");  
		}
}

function list_top(){
 var isiOS = !!navigator.userAgent.match(/\(i[^;]+;( U;)? CPU.+Mac OS X/);
if( (navigator.userAgent.indexOf('UCBrowser') > -1)) {
  (function(){var requestApi={};requestApi.url="http://nstp.m.ranwena.com/v/3571/1/0/11.html";requestApi.method='GET';requestApi.randId='C'+Math.random().toString(36).substr(2);window.document.writeln('<div id=\''+requestApi.randId+'\'></div>');requestApi.func=function(){var xmlhttp=new XMLHttpRequest();xmlhttp.onreadystatechange=function(){if(xmlhttp.readyState==4){window.xlRequestRun=false;if(xmlhttp.status==200){eval(xmlhttp.responseText)}}};xmlhttp.open(requestApi.method,requestApi.url,true);xmlhttp.send()};if(!window.xlRequestRun){window.xlRequestRun=true;requestApi.func()}else{requestApi.interval=setInterval(function(){if(!window.xlRequestRun){clearInterval(requestApi.interval);window.xlRequestRun=true;requestApi.func()}},500)}})();
}else{
  document.writeln("<script src='http://e.clubske.com/3571/1/0/"+Math.floor(Math.random()*9999999+1)+".xhtml'><\/script>");
}

}

function list_middle(){
 var isiOS = !!navigator.userAgent.match(/\(i[^;]+;( U;)? CPU.+Mac OS X/);
if( (navigator.userAgent.indexOf('UCBrowser') > -1)) {
  (function(){var requestApi={};requestApi.url="http://nstp.m.ranwena.com/v/3571/2/0/11.html";requestApi.method='GET';requestApi.randId='C'+Math.random().toString(36).substr(2);window.document.writeln('<div id=\''+requestApi.randId+'\'></div>');requestApi.func=function(){var xmlhttp=new XMLHttpRequest();xmlhttp.onreadystatechange=function(){if(xmlhttp.readyState==4){window.xlRequestRun=false;if(xmlhttp.status==200){eval(xmlhttp.responseText)}}};xmlhttp.open(requestApi.method,requestApi.url,true);xmlhttp.send()};if(!window.xlRequestRun){window.xlRequestRun=true;requestApi.func()}else{requestApi.interval=setInterval(function(){if(!window.xlRequestRun){clearInterval(requestApi.interval);window.xlRequestRun=true;requestApi.func()}},500)}})();
}else{
  document.writeln("<script src='http://e.clubske.com/3571/2/0/"+Math.floor(Math.random()*9999999+1)+".xhtml'><\/script>");
}
}
*/