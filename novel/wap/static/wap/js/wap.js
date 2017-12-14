
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
};


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
    }
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

function Paginator() {
    var cur_url = window.location.href;
    var page = document.getElementById("page_num").value;
    if(isNaN(page) || page.length == 0){page="1";}
    if(cur_url.indexOf('-') > -1){
        location.href = cur_url.substring(0, cur_url.indexOf('-')+1) + page + '/';
    }else{
        location.href = cur_url.substring(0, cur_url.length-1) + "/page-" + page + '/';
    }
}


function goToPaginator() {
    var cur_url = window.location.href;
    location.href = cur_url.substring(0, cur_url.length-1) + "/page-1/";
}

$(document).ready(function(){
    $('#id_affirm_password').blur(function(){
        if ($('#id_affirm_password').val() == $('#id_password').val()){
            $('#submit_button').removeAttr('disabled');
        } else{
            alert('两次密码不一致');
            $('#submit_button').attr('disabled', 'disabled');
        }
    });
});


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
