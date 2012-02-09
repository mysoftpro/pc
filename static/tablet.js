_.templateSettings = {
    interpolate : /\{\{(.+?)\}\}/g
    ,evaluate: /\[\[(.+?)\]\]/g
};
var localCart = {
    items:{},
    price:0,
    getTag:function(jel){
        return jel[0].tagName.toLowerCase();
    },
    addItem:function(e){
        var target = $(e.target);
        var _id;
        var tag=  this.getTag(target);
        while (tag !== 'ul'){
            if (tag == 'li')
                _id = target.attr('id');
            target = target.parent();
            tag = this.getTag(target);
        }
        var catalog = target.attr('id');
        this.items[catalog] = _id;
        this.renderItem(catalog);
    },
    renderItem:function(catalog){
        var item = bindings[catalog][this.items[catalog]];
        var tot = $('#videoprice').find('tr').last();
        var row = $('#cat'+catalog);
        if (row.length==0){
	    $('#video_top').css('height',$('#video_top').height()+25);
            tot.before('<tr id="cat'+catalog+'"><td></td><td>1 шт</td><td> р.</td></tr>');
            row = tot.prev();
        }
        var childs = row.children();
        childs.first().text(item.name);
        childs.last().text(item.price+' р.');
        var total = price;
        var items = this.items;
        _(items).chain().keys().each(function(key){
                                              if (key==tablet_catalog)return;
                                              total +=	bindings[key][items[key]].price;
                                 });
        tot.children().last().text(total+' р.');	
    }
};

(function init(){
     localCart.price = price;
     localCart.items[tablet_catalog] = _id;
     var uls = $('ul.chipVendors');
     uls.find('li').click(function(e){
                                     var target = $(e.target);
                                     var tag = target[0].tagName.toLowerCase();
                                     if(tag=='span')
                                         return;
                                     var guard = 10;
                                     while(tag!=='li'){
                                    target = target.parent();
                                         tag = target[0].tagName.toLowerCase();
                                     }
                                     showComponent({preventDefault:function(){},
                                               target:{id:'_'+target[0].id}});
                                 });
     $('.videoadd').click(function(e){localCart.addItem(e);});
         $('#tocart').click(function(){			   
			   $.ajax({
				      url:'/saveset',
				      data:{data:JSON.stringify(localCart.items)},
				      success:function(data){
					  if (data=="ok"){
					      var cart_el = $('#cart');
					      if (cart_el.length>0){
						  cart_el.text('Корзина('+$.cookie('pc_cart')+')');
					      }
					      else{
						  $('#main_menu')
						      .append(_.template('<li><a id="cart" href="/cart/{{cart}}">Корзина(1)</a></li>',{cart:$.cookie('pc_user')}));

					      }
					      alert('Получилось!');
					  }
					  else
					      alert('Что-то пошло не так =(');
				      }
				  });
		       });
})();
