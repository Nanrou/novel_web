function setCookie(c_name,value,expiredays)//设置cookie
{   
    var expiredays=expiredays||30;
    var exdate=new Date();//生成当时的时间
    exdate.setDate(exdate.getDate()+expiredays); //时间加上30天 
    document.cookie=c_name+ "=" +escape(value)+";expires="+exdate.toUTCString()+";";
    //escape是编码字符串（编码URL有专门的encodeURL），toGMTString已经弃用，改成UTC，paths的默认位置就是/
}

function getCookie(c_name)//拿到某个name的值
{
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
}

function delCookie(name){//只需要设置 expires 参数为以前的时间即可
    var exp = new Date();
    exp.setTime(exp.getTime() - 1);
    var cval=getCookie(name);
    document.cookie= name + "=;expires="+exp.toGMTString();
}

//updown
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
    fq = setTimeout("up()", 50)}; //每隔50ms就会调用自身
function dn() {
    $wd = $(window);
    $wd.scrollTop($wd.scrollTop() + 1);
    fq = setTimeout("dn()", 50)}; 