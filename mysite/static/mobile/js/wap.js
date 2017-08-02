
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

function goToPaginator() {
    var cur_url = window.location.href;
    var page = document.getElementById("page_num").value;
    if(isNaN(page) || page.length == 0){page="1";}
    if(cur_url.indexOf('-') > -1){
        location.href = cur_url.substring(0, cur_url.indexOf('-')+1) + page + '/';
    }else{
        location.href = cur_url.substring(0, cur_url.length-1) + "-" + page + '/';
    }
}

