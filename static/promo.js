var skin = document.location.search.match('skin');
$('#promostuff td').click(function(e){
			      if (!skin)
				  $('td').css('color','#ddd');
			      else
				  $('td').css('color','#333');
			      var target = $(e.target);
			      var tr = target.parent();
			      if (!skin)
				  tr.children().css('color','#aadd00');
			      else
				  tr.children().css('color','#B47A00');
			      var c = components[tr.attr('id')];
			      var p = $('#promo_description p');
			      p.parent().css('opacity','0.0');
			      p.html(c['description']);
			      while(p.next().length>0)
				  p.next().remove();
			      $('#promo_image img').attr('src','/image/'+_id+'/'+c['top_image']);
			      p.parent().animate({'opacity':'1.0'},500);

			  });
$('#to_cart').click(function(e){
			var mother_code = _(components)
			    .chain()
			    .keys()
			    .select(function(key){
					return components[key]['type']=='mother';
				    })
			    .first()
			    .value();
			var proc_code = _(components)
			    .chain()
			    .keys()
			    .select(function(key){
					return components[key]['type']=='proc';
				    })
			    .first()
			    .value();

			var items=  {};
			_(components)
			    .chain().keys().each(function(key){
						     var cat = parts[components[key]['type']];
						     if (cat)
							 items[cat] = key;
					      }).value();
			$.ajax({
				   url:'/catalogs_for?c='+mother_code+'&c='+proc_code,
				   success:function(data){
				       var model = {};
				       model['mother_catalogs'] = data[mother_code];
				       model['proc_catalogs'] = data[proc_code];
				       model['items'] = items;
				       model['dvd'] = true;
				       model['building'] = true;
				       model['installing'] = true;
				       model['promo'] = true;
				       model['name'] = $('h1').text();
				       model['title'] = $('#promo_title').text();
				       model['description'] = $('#promo_desc').text();
				       model['parent'] = $('#promo_desc').text();
				       model['parent'] = _(document.location.href.split('/'))
					   .last().split('?')[0];
				       var to_send = {model:JSON.stringify(model)};
				       $.ajax({
						  url:'/save',
						  data:to_send,
						  success:function(){
						      alert('Получилось!');
						      var cart_el = $('#cart');
						      if (cart_el.length>0){
							  cart_el.text('Корзина('+$.cookie('pc_cart')+')');
						      }
						      else{
							  if (!data['edit'])
							      $('#main_menu')
							      .append(_.template('<li><a id="cart" href="/cart/{{cart}}">Корзина(1)</a></li>',
										 {
										     cart:$.cookie('pc_user')
										 }));
						      }
						  }
					      });
				   }
			       });
		    });
$('#promostuff td').first().click();
//$('body').append('<div id="image_storage"></div>');