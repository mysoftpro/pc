function init(){
    $('.chipVendors li').click(function(e){
				   var target = $(e.target);
				   var tag = target[0].tagName.toLowerCase();
				   if(tag=='a')
				       return;
				   var guard = 10;
				   while(tag!=='li'){
				       target = target.parent();
				       tag = target[0].tagName.toLowerCase();
				   }
				   console.log(target[0].id);
				   showComponent({preventDefault:function(){},target:target[0]});
			       });
}
init();