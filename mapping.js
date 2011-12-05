function getTrs(){
    var trs = $('colgroup').next().find('tr');
    var clean_trs = [];
    for (var i=0;i<trs.length;i++){
	var tr = $(trs.get(i));
	if (tr.attr('id').match('bx_'))
	    clean_trs.push(tr);
    }
    return clean_trs;
}

var gmap = {};
var clean_trs = getTrs();
for(var i=0;i<clean_trs.length;i++){
    gmap[i] = {tr:clean_trs[i]};
}
function get(i){
    console.log(gmap[i].tr.children().last().find('a').text());
}
function set(i, code){
    var _id = gmap[0].tr.attr('id').split('_')[2];
    gmap[i]['nc'] = document.location.href+_id+'/';
    gmap[i]['wc'] = code;
    has(i);
}
function has(i){
    console.log(gmap[i]);
}
function save(){
    for (var ob in gmap){
	if (!ob.wc || !ob.nc)
	    continue;
	$.ajax({
		   url:'/map?key=218b47411d2394b78810f7baaa000328&op=set&wc='+ob.wc+'&nc='+ob.nc,
		   success:function(answer){
		       console.log(answer);
		   }
	       });
    }
}
