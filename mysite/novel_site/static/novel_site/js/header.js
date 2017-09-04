
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
    //var exdate=new Date();//生成当时的时间
    //exdate.setDate(exdate.getDate()+expiredays); //时间加上30天 
    //document.cookie=c_name+ "=" +escape(value)+";expires="+exdate.toUTCString()+";";
    //escape是编码字符串（编码URL有专门的encodeURL），toGMTString已经弃用，改成UTC，paths的默认位置就是/
	$.cookie(c_name, value, {expires: expiredays, path:'/'})
}

function getCookie(c_name)//拿到某个name的值
{
	/*
    if (document.cookie.length>0){//若没有cookie则直接返回空
        c_start=document.cookie.indexOf(c_name + "=");//找到目标name的起始位置
        if (c_start!=-1){ 
            c_start=c_start + c_name.length+1;//然后定位到等号的位置
            c_end=document.cookie.indexOf(";",c_start);//从等号位置开始去找最近的分号
            if (c_end==-1) c_end=document.cookie.length;
            return unescape(document.cookie.substring(c_start,c_end));//substring是按位置截取部分字符串
        } 
    }
    return "";
	*/
	return $.cookie(c_name);
}

function delCookie(name){//只需要设置 expires 参数为以前的时间即可
    var exp = new Date();
    exp.setTime(exp.getTime() - 1);
    var cval=getCookie(name);
    document.cookie= name + "=;expires="+exp.toGMTString();
}
//设置主页
function SetHome(obj,vrl)
    {
        try
        {
            obj.style.behavior='url(#default#homepage)';obj.setHomePage(vrl);
        }
        catch(e){
                if(window.netscape) {
                        try {
                                netscape.security.PrivilegeManager.enablePrivilege("UniversalXPConnect"); 
                        } 
                        catch (e) { 
                                alert("此操作被浏览器拒绝！\n请在浏览器地址栏输入“about:config”并回车\n然后将[signed.applets.codebase_principal_support]设置为'true'"); 
                        }
                        var prefs = Components.classes['@mozilla.org/preferences-service;1'].getService(Components.interfaces.nsIPrefBranch);
                        prefs.setCharPref('browser.startup.homepage',vrl);
                 }
        }
    }
//添加收藏
function addFavorite() {
    var url = window.location;
    var title = document.title;
    var ua = navigator.userAgent.toLowerCase();
    if (ua.indexOf("360se") > -1) {
        alert("由于360浏览器功能限制，请按 Ctrl+D 手动收藏！");
    }
    else if (ua.indexOf("msie 8") > -1) {
        window.external.AddToFavoritesBar(url, title); //IE8
    }
    else if (document.all) {
		try{
			window.external.addFavorite(url, title);
		}catch(e){
			alert('您的浏览器不支持,请按 Ctrl+D 手动收藏!');
		}
	}
	else if (window.sidebar) {
		window.sidebar.addPanel(title, url, "");
	}
	else {
	alert('您的浏览器不支持,请按 Ctrl+D 手动收藏!');
	}
}
//lastread
function show_lastread() {
	var title = $.cookie('lastread_title');
	var url = $.cookie('lastread_url');
	if (!title) {
		return '';
	}
	var tmp = '<div class="nav_lastread"><div>你上次看到这里了： <a href="{u}">{t}</a></div></div>'.format({t:title, u:url});
	document.write(tmp);
}

//updown，就是那个滑动插件的
jQuery(document).ready(function($) {
    $body = (window.opera) ? //判断浏览器是不是opera
        (document.compatMode == "CSS1Compat" ? $("html") : $("body")) 
        : $("html,body");
    $("#shang").mouseover(function() {
        up()})
        .mouseout(function() {
            clearTimeout(fq)})  //取消掉那个定时器
        .click(function() {
            $body.animate({scrollTop: 0},400)});
    $("#xia").mouseover(function() {
        dn()})
        .mouseout(function() {
            clearTimeout(fq)})
        .click(function() {
            $body.animate({scrollTop: $(document).height()},400)});
    $("#comt").click(function() {
        $body.animate({scrollTop: $("#content").offset().top},400)});});
function up() {  //一旦启动就进入自调用模式了
    $wd = $(window);
    $wd.scrollTop($wd.scrollTop() - 1);
    fq = setTimeout("up()", 50)} //每隔50ms就会调用自身
function dn() {
    $wd = $(window);
    $wd.scrollTop($wd.scrollTop() + 1);
    fq = setTimeout("dn()", 50)}


$(document).ready(function(){
    $('.captcha').click(function(){
        $.ajax({
            url: '/refresh_captcha',
            success: function(result){
                $('.captcha').attr('src', result['new_cptch_image']);
                $('#id_captcha_0').attr('value', result['new_cptch_key']);
            }
        });
    });
});

function add_book(){
    var ll = window.location.href.split('/');
    var book_id = ll[ll.length - 2];

    $.ajax({
        url: '/add_book/' + book_id + '/',
        success: function(result){
            if (result['status'] == 'success'){
                $('#collect_book').attr('onclick', 'remove_book()').text('取消收藏');
                alert('已成功添加到书架')
            } else {
                $(location).attr('pathname', result['uri'])
            }
        }
    });
}


function remove_book(){
    var ll = window.location.href.split('/');
    var book_id = ll[ll.length - 2];

    $.ajax({
        url: '/remove_book/' + book_id + '/',
        success: function(result) {
            if (result['status'] == 'success') {
                $('#collect_book').attr('onclick', 'add_book()').text('加入收藏');
                alert('已移除出书架')
            }
        }})
}


$(document).ready(function(){     检测两次输入是否相同
    $('#submit_button').click(function(){
        $.ajax({
            url: '/refresh_captcha',
            success: function(result){
                $('.captcha').attr('src', result['new_cptch_image']);
                $('#id_captcha_0').attr('value', result['new_cptch_key']);
            }
        });
    });
});
