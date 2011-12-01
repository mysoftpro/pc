$('#promostuff td').click(function(e){
			      $('td').css('color','#ddd');
			      var target = $(e.target);
			      //target.css('color','#aadd00');
			      var tr = target.parent();
			      tr.children().css('color','#aadd00');
			      var c = components[tr.attr('id')];
			      var p = $('#promo_description p');
			      p.html(c['description']);
			      while(p.next().length>0)
				  p.next().remove();
			      $('#promo_image img').attr('src','/image/'+_id+'/'+c['top_image']);
			      if (c['bottom_images'])
				  _(c['bottom_images']).each(function(img){
								 p.after('<img src="/image/'+
									  _id+'/'+img+'"/>');
							     });

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

var to_send = {model:'{"mother_catalogs":["7363","7388","17961"],"proc_catalogs":["7363","7399","18027"],"items":{"7388":"19338","7406":"20122","7383":"19165","7396":null,"7399":"19734","7387":"13086","7390":"13677","7369":"17398","7384":"19777","7389":"11760","7394":"19810"},"installing":true,"building":true,"dvd":true,"parent":"202da260"}'};

// {"_id":"ajax","_rev":"121-2a99f8de1c9ec0ef528d06f4da6b8039","name":"\u0410\u044f\u043a\u0441","our_price":23900,"components":[{"code":"19208","name":"\u041a\u043e\u0440\u043f\u0443\u0441 Delux DLC-MQ827","top_image":"deluxe.png","type":"case","order":10,"description":"\u041e\u0442\u043b\u0438\u0447\u043d\u044b\u0439 \u043a\u043e\u0440\u043f\u0443\u0441, \u043f\u043e\u043a\u0440\u0430\u0448\u0435\u043d\u043d\u044b\u0439 \u0441\u043d\u0443\u0440\u0443\u0436\u0438 \u0438 \u0438\u0437\u043d\u0443\u0442\u0440\u0438.\u041f\u0440\u043e\u0434\u0443\u043c\u0430\u043d\u043d\u0430\u044f \u0430\u044d\u0440\u043e\u0434\u0438\u043d\u0430\u043c\u0438\u043a\u0430 \u0434\u043b\u044f \u043f\u043e\u0432\u044b\u0448\u0435\u043d\u043d\u043e\u0433\u043e \u043e\u0445\u043b\u0430\u0436\u0434\u0435\u043d\u0438\u044f \u0438 \u0448\u0443\u043c\u043e\u043f\u043e\u0434\u0430\u0432\u043b\u0435\u043d\u0438\u044f. \u0411\u043b\u043e\u043a \u043f\u0438\u0442\u0430\u043d\u0438\u044f 600W \u0447\u0442\u043e\u0431\u044b \u0437\u0430\u0440\u0430\u043d\u0435\u0435 \u043f\u043e\u043a\u0440\u044b\u0442\u044c \u0432\u0441\u0435 \u0432\u043e\u0437\u043c\u043e\u0436\u043d\u044b\u0435 \u043f\u043e\u0442\u0440\u0435\u0431\u043d\u043e\u0441\u0442\u0438 \u0432\u0430\u0448\u0438\u0445 usb \u0443\u0441\u0442\u0440\u043e\u0439\u0441\u0442\u0432 \u0438 \u0432\u0438\u0434\u0435\u043e\u043a\u043e\u043d\u0442\u0440\u043e\u043b\u043b\u0435\u0440\u043e\u0432."},{"code":"19992","name":"\u041c\u0430\u0442\u0435\u0440\u0438\u043d\u0441\u043a\u0430\u044f \u043f\u043b\u0430\u0442\u0430 GIGABYTE GA-A55M-S2V","top_image":"GIGABYTE-Motherboard-GA-A55M-S2V.png","type":"mother","order":20,"description":"\u041d\u043e\u0432\u0435\u0439\u0448\u0430\u044f \u043c\u0430\u0442\u0435\u0440\u0438\u043d\u0441\u043a\u0430\u044f \u043f\u043b\u0430\u0442\u0430 \u043f\u043e\u0434\u0434\u0435\u0440\u0436\u0438\u0432\u0430\u0435\u0442 \u0442\u0435\u0445\u043d\u043e\u043b\u043e\u0433\u0438\u044e CrossFire, \u0442\u0430\u043a \u0447\u0442\u043e \u0432\u044b \u0441\u043c\u043e\u0436\u0435\u0442\u0435 \u0434\u043e\u0431\u0430\u0432\u0438\u0442\u044c \u0432 \u0441\u0438\u0441\u0442\u0435\u043c\u0443 \u0432\u0442\u043e\u0440\u0443\u044e \u0432\u0438\u0434\u0435\u043e\u043a\u0430\u0440\u0442\u0443 \u0438 \u0433\u0435\u043d\u0435\u0440\u0438\u0440\u043e\u0432\u0430\u0442\u044c \u043a\u0430\u0440\u0442\u0438\u043d\u043a\u0443 \u0434\u0432\u0443\u043c\u044f \u0432\u0438\u0434\u0435\u043e\u043a\u0430\u0440\u0442\u0430\u043c\u0438 \u043f\u0430\u0440\u0430\u043b\u043b\u0435\u043b\u044c\u043d\u043e. 6 \u043a\u0430\u043d\u0430\u043b\u043e\u0432 Sata \u0438 \u0432\u0441\u0442\u0440\u043e\u0435\u043d\u043d\u044b\u0439 raid \u043a\u043e\u043d\u0442\u0440\u043e\u043b\u043b\u0435\u0440. \u0422\u0435\u0445\u043d\u043e\u043b\u043e\u0433\u0438\u0438 \u043f\u043e\u043d\u0438\u0436\u0435\u043d\u0438\u044f \u0448\u0443\u043c\u0430 \u0438 \u044d\u043d\u0435\u0440\u0433\u043e\u043f\u043e\u0442\u0440\u0435\u0431\u043b\u0435\u043d\u0438\u044f."},{"code":"20017","name":"\u041f\u0440\u043e\u0446\u0435\u0441\u0441\u043e\u0440 AMD A4 X2 3300 2,5 \u0413\u0413\u0446","top_image":"amd_a4_x2.png","type":"proc","order":30,"description":"\u041d\u043e\u0432\u0435\u0439\u0448\u0438\u0439 \u043f\u0440\u043e\u0446\u0435\u0441\u0441\u043e\u0440 A4-3300 \u043f\u043e\u043c\u0438\u043c\u043e \u0434\u0432\u0443\u0445 \u044f\u0434\u0435\u0440 \u0438\u043c\u0435\u0435\u0442 \u0432\u0441\u0442\u0440\u043e\u0435\u043d\u043d\u043e\u0435 \u0432\u0438\u0434\u0435\u043e\u044f\u0434\u0440\u043e, \u043a\u043e\u0442\u043e\u0440\u043e\u0435 \u0440\u0430\u0431\u043e\u0442\u0430\u0435\u0442 \u0432 \u043f\u0430\u0440\u0430\u043b\u043b\u0435\u043b\u044c \u0441 \u0432\u0438\u0434\u0435\u043e\u043a\u0430\u0440\u0442\u043e\u0439 \u043f\u043e \u0442\u0435\u0445\u043d\u043e\u043b\u043e\u0433\u0438\u0438 AMD Dual Graphics."},{"code":"19470","name":"HD6450 XFX 1GB DDR3 DVI+VGA+HDMI BOX HD-645X-ZNH2","bottom_images":["eyefinity.png","appaceleration.png"],"top_image":"hd6450.png","type":"video","order":40,"description":"\u0427\u0438\u043f\u0441\u0435\u0442 HD6450 \u043f\u043e\u0434\u0434\u0435\u0440\u0436\u0438\u0432\u0430\u0435\u0442 \u0442\u0435\u0445\u043d\u043e\u043b\u043e\u0433\u0438\u0438 AMD HD3D Technology, AMD Accelerated Parallel Processing Technology, AMD PowerPlay TechnologyAMD Eyefinity Technology \u041f\u043e\u0437\u0432\u043e\u043b\u044f\u0435\u0442 \u043f\u043e\u0434\u043a\u043b\u044e\u0447\u0430\u0442\u044c \u0434\u043e 5 \u0434\u0438\u0441\u043f\u043b\u0435\u0435\u0432. \u041f\u043e\u043b\u043d\u0430\u044f \u0430\u043f\u043f\u0430\u0440\u0430\u0442\u043d\u0430\u044f \u043f\u043e\u0434\u0434\u0435\u0440\u0436\u043a\u0430 DirectX\u00ae 11. \u0412\u043e\u0437\u043c\u043e\u0436\u043d\u043e\u0441\u0442\u044c \u0434\u043e\u0431\u0430\u0432\u0438\u0442\u044c \u0432\u0442\u043e\u0440\u0443\u044e \u043a\u0430\u0440\u0442\u0443 \u0438 \u0440\u0430\u0431\u043e\u0442\u0430\u0442\u0430\u0442\u044c \u043f\u0430\u0440\u0430\u043b\u043b\u0435\u043b\u044c\u043d\u043e \u0441 \u0442\u0435\u0445\u043d\u043e\u043b\u043e\u0433\u0438\u0435\u0439 CrossFire. \u0420\u0430\u0431\u043e\u0442\u0430\u0435\u0442 \u043f\u0430\u0440\u0430\u043b\u043b\u0435\u044c\u043d\u043e \u0441 APU \u0441\u0435\u0440\u0438\u0438 A \u043f\u043e \u0442\u0435\u0445\u043d\u043e\u043b\u043e\u0433\u0438\u0438 AMD Dual Graphics."},{"code":"15318","name":"\u0416\u0435\u0441\u0442\u043a\u0438\u0439 \u0434\u0438\u0441\u043a 1000GB WD GreenPower Sata2 64mb WD10EARS","top_image":"WD_GreenPower.png","type":"hdd","order":40,"description":"\u0416\u0435\u0441\u0442\u043a\u0438\u0439 \u0434\u0438\u0441\u043a Western Digital - \u043b\u0443\u0447\u0448\u0435\u0435 \u043f\u0440\u0435\u0434\u043b\u043e\u0436\u0435\u043d\u0438\u0435 \u043d\u0430 \u0440\u044b\u043d\u043a\u0435. \u0421\u0430\u043c\u044b\u0439 \u0431\u043e\u043b\u044c\u0448\u043e\u0439 \u043a\u044d\u0448: 64Mb \u043e\u0431\u0435\u0441\u043f\u0435\u0447\u0438\u0442 \u043c\u0430\u043a\u0438\u0441\u043c\u0430\u043b\u044c\u043d\u0443\u044e \u0441\u043a\u043e\u0440\u043e\u0441\u0442\u044c."},{"code":"19575","name":"\u041e\u0417\u0423 2X DDR3 4096MB Crucial Rendition CL9 1333 PC3-10600","top_image":"crucial.png","type":"ram","order":40,"description":"\u041f\u0430\u043c\u044f\u0442\u0438 \u043c\u043d\u043e\u0433\u043e \u043d\u0435 \u0431\u044b\u0432\u0430\u0435\u0442. \u0412 \u044d\u0442\u043e\u043c \u043a\u043e\u043c\u043f\u044c\u044e\u0442\u0435\u0440\u0435 \u0435\u0435 \u043a\u043e\u043b\u0438\u0447\u0435\u0441\u0442\u0432\u0430 \u0445\u0432\u0430\u0442\u0438\u0442 \u0441 \u0438\u0437\u0431\u044b\u0442\u043a\u043e\u043c \u043d\u0430 \u0432\u044b\u043f\u043e\u043b\u043d\u0435\u043d\u0438\u0435 \u043b\u044e\u0431\u044b\u0445 \u0432\u0430\u0448\u0438\u0445 \u0437\u0430\u0434\u0430\u0447."},{"code":"18692","name":"\u0410\u043a\u0443\u0441\u0442\u0438\u0447\u0435\u0441\u043a\u0430\u044f \u0441\u0438\u0441\u0442\u0435\u043c\u0430 Genius SW-M2.1 350, 11W black","top_image":"genius.png","type":"audio","order":40,"description":"Audio"},{"code":"18932","name":"\u0414\u0438\u0441\u043a\u043e\u0432\u043e\u0434 DVD-RW Samsung SH-222AB/BEBE Sata","bottom_images":["f1.jpg","f3.jpg"],"top_image":"samsung.png","type":"dvd","order":40,"description":"Dvd"},{"code":"17705","name":"\u041c\u043e\u043d\u0438\u0442\u043e\u0440 LED BenQ GL2240 21.5\"/5ms/250","top_image":"24293_big.png","type":"display","order":40,"description":"\u041e\u043d \u043e\u0447\u0435\u043d\u044c \u0431\u043e\u043b\u044c\u0448\u043e\u0439. \u0422\u0435\u0445\u043d\u043e\u043b\u043e\u0433\u0438\u044f LED - \u043f\u043e\u0434\u0441\u0442\u0432\u0435\u0442\u043a\u0430 \u044d\u043a\u0440\u0430\u043d\u0430 \u0438\u0437\u043d\u0443\u0442\u0440\u0438 - \u043e\u0433\u0440\u043e\u043c\u043d\u044b\u0439 \u0441\u043a\u0430\u0447\u043e\u043a \u0432\u043f\u0435\u0440\u0435\u0434 \u043f\u043e \u0441\u0440\u0430\u0432\u043d\u0435\u043d\u0438\u044e \u0441 LCD \u043c\u043e\u043d\u0438\u0442\u043e\u0440\u0430\u043c\u0438. \u041a\u0430\u0440\u0442\u0438\u043d\u043a\u0430 \u0441\u043e\u0447\u043d\u0435\u0435. \u0412 \u043d\u0435\u0439 \u043d\u0435\u0442 \"\u043f\u0440\u043e\u0432\u0430\u043b\u043e\u0432\" \u0446\u0432\u0435\u0442\u0430 \u0438 \u043d\u0435\u043f\u043e\u043d\u044f\u0442\u043d\u044b\u0445 \u0431\u043b\u0438\u043a\u043e\u0432 \u043a\u0430\u043a \u0432 \u0441\u0442\u0430\u0440\u044b\u0445 \u043c\u043e\u043d\u0438\u0442\u043e\u0440\u0430\u0445. \u0413\u043e\u0440\u0430\u0437\u0434\u043e \u0432\u044b\u0448\u0435 \u043a\u043e\u043d\u0442\u0440\u0430\u0441\u0442 \u0434\u0438\u043d\u0430\u043c\u0438\u043d\u043e\u0433\u043e \u0438\u0437\u043e\u0431\u0440\u0430\u0436\u0435\u043d\u0438\u044f."},{"code":"17398","name":"\u041f\u041e Microsoft Win 7 Home Basic 64-bit Rus CIS SP1","top_image":"windows_7.png","type":"windows","order":40,"description":"Windows - \u044d\u0442\u043e \u0442\u043e, \u0447\u0442\u043e \u0441\u0432\u044f\u0436\u0435\u0442 \u0432\u043c\u0435\u0441\u0442\u0435 \u0432\u0441\u0435 \u043a\u043e\u043c\u043f\u043e\u043d\u0435\u043d\u0442\u044b \u0432 \u0435\u0434\u0438\u043d\u0443\u044e \u043d\u0430\u0434\u0435\u0436\u043d\u0443\u044e \u0441\u0438\u0441\u0442\u0435\u043c\u0443. \u0412\u044b \u0437\u0430\u0431\u0443\u0434\u0435\u0442\u0435 \u043f\u0440\u043e \u0437\u0430\u0432\u0438\u0441\u0430\u043d\u0438\u044f, \u0441\u0438\u043d\u0438\u0435 \u044d\u043a\u0440\u0430\u043d\u044b \u0438 \u0432\u0438\u0440\u0443\u0441\u043d\u044b\u0435 \u0431\u0430\u043d\u043d\u0435\u0440\u044b. \u0421\u0435\u043c\u0435\u0440\u043a\u0430 \u0440\u0430\u0431\u043e\u0442\u0430\u0435\u0442 \u0447\u0435\u0442\u043a\u043e \u0438 \u0441\u0442\u0430\u0431\u0438\u043b\u044c\u043d\u043e. \u041c\u043e\u0436\u043d\u043e \u043d\u0435 \u0432\u044b\u043a\u043b\u044e\u0447\u0430\u0442\u044c \u043a\u043e\u043c\u043f\u044c\u044e\u0442\u0435\u0440 \u043c\u0435\u0441\u044f\u0446\u0430\u043c\u0438."}],"link_to_dual_graphics":"http://www.amd.com/us/products/technologies/dual-graphics/pages/dual-graphics.aspx#3","title":"\u0421\u043e\u0432\u0440\u0435\u043c\u0435\u043d\u043d\u044b\u0439 \u043a\u043e\u043c\u043f\u044c\u044e\u0442\u0435\u0440 \u043d\u0430 \u0431\u0430\u0437\u0435 \u043d\u043e\u0432\u0435\u0439\u0448\u0435\u0439 \u043f\u043b\u0430\u0442\u0444\u043e\u0440\u043c\u044b AMD","description":"\u042d\u0442\u043e\u0442 \u043a\u043e\u043c\u043f\u044c\u044e\u0442\u0435\u0440 \u0441\u043e\u0431\u0440\u0430\u043d \u043d\u0430 \u043f\u043b\u0430\u0442\u0444\u043e\u0440\u043c\u0435 AMD, \u0443\u0441\u0442\u0440\u043e\u0439\u0441\u0442\u0432\u0430 \u0434\u043b\u044f \u043a\u043e\u0442\u043e\u0440\u043e\u0439 \u0432\u044b\u043f\u0443\u0441\u043a\u0430\u044e\u0442\u0441\u044f \u0441 \u0438\u044e\u043b\u044f \t\u043c\u0435\u0441\u044f\u0446\u0430 \u044d\u0442\u043e\u0433\u043e \u0433\u043e\u0434\u0430.","extra":"\u0432 \u043a\u0430\u0447\u0435\u0441\u0442\u0432\u0435 \u0434\u043e\u043c\u0430\u0448\u043d\u0435\u0439 \u043c\u0443\u043b\u044c\u0442\u0438\u043c\u0435\u0434\u0438\u0439\u043d\u043e\u0439 \u0441\u0442\u0430\u043d\u0446\u0438\u0438 \u0438 \u0434\u043b\u044f \u0438\u0433\u0440.","_attachments":{"appaceleration.png":{"content_type":"image/png","revpos":23,"digest":"md5-CfrCiOo04AkqYPx+WbKXLQ==","length":56024,"stub":true},"f3.jpg":{"content_type":"image/jpeg","revpos":80,"digest":"md5-pKgYdIZf/u60fhMVFdMSnQ==","length":39969,"stub":true},"WD_GreenPower.png":{"content_type":"image/png","revpos":98,"digest":"md5-eBAl4Cvh/QwW/ERwmDZGmQ==","length":98585,"stub":true},"f1.jpg":{"content_type":"image/jpeg","revpos":79,"digest":"md5-KUUFVk4lyUl8eQDqBx69Tg==","length":36258,"stub":true},"GIGABYTE-Motherboard-GA-A55M-S2V.png":{"content_type":"image/png","revpos":48,"digest":"md5-ytyg9hdorKZwZc28q+W3mg==","length":150048,"stub":true},"crucial.png":{"content_type":"image/png","revpos":57,"digest":"md5-T6zgQzCRWP9RdVUk3o99Zg==","length":158121,"stub":true},"samsung.png":{"content_type":"image/png","revpos":95,"digest":"md5-D+HDTFcSwwM99bZjrjR0Mg==","length":94463,"stub":true},"24293_big.png":{"content_type":"image/png","revpos":86,"digest":"md5-zLd72zpYv9LbVpzqNJvRoA==","length":82262,"stub":true},"amd_a4_x2.png":{"content_type":"image/png","revpos":50,"digest":"md5-hS1CphuGfK9iU5sMtAkwLg==","length":157029,"stub":true},"deluxe.png":{"content_type":"image/png","revpos":16,"digest":"md5-fmk1GNISFmJWIr3ZhESSZg==","length":32051,"stub":true},"eyefinity.png":{"content_type":"image/png","revpos":18,"digest":"md5-818amsDJSskXvaFok2VSUQ==","length":37193,"stub":true},"windows_7.png":{"content_type":"image/png","revpos":65,"digest":"md5-x/y6kUrZ1ztnRP1yM1VF+g==","length":133961,"stub":true},"hd6450.png":{"content_type":"image/png","revpos":44,"digest":"md5-rNvob351sp+CNaMsGpfRug==","length":98431,"stub":true},"genius.png":{"content_type":"image/png","revpos":92,"digest":"md5-qoybtKRBv8qeLfn4tahrJw==","length":109870,"stub":true}}}
