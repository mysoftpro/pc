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
			var codes = _(components)
			    .chain()
			    .keys()
			    .select(function(key){
					return components[key]['type']!='dvd';
				    })
			    .value()
			    .join('&c=');
			$.ajax({
				   url:'/catalogs_for?c='+codes,
				   success:function(data){
				       var to_send = {};
				       to_send['mother_catalogs'] = data[mother_code];
				       to_send['proc_catalogs'] = data[proc_code];
				       console.log(data);
				   }
			       });
		    });

var to_send = {model:'{"mother_catalogs":["7363","7388","17961"],"proc_catalogs":["7363","7399","18027"],"items":{"7388":"19338","7406":"20122","7383":"19165","7396":null,"7399":"19734","7387":"13086","7390":"13677","7369":"17398","7384":"19777","7389":"11760","7394":"19810"},"installing":true,"building":true,"dvd":true,"parent":"202da260"}'};