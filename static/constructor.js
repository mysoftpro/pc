//TODO
//checkMother!
//checkProc!
_.templateSettings = {
    interpolate : /\{\{(.+?)\}\}/g
    ,evaluate: /\[\[(.+?)\]\]/g
};

var Component = Backbone
    .Model
    .extend({
		initialize:function(){
		    var id = this.id;
		    var storage = this.get('storage');
		    var doc = _(storage)
			.chain()
			.select(function(doc){
				    return doc['_id']==id;})
			.first()
			.value();
		    if (!doc)
			doc = {};
		    this.set('doc',doc);
		    _.bindAll(this, "getIcon", "cheaperBetter");
		},
		getIcon:function(){
		    var doc = this.get('doc');
		    var retval = '/static/no_image.jpg';
		    if (doc && doc['imgs'] && doc['imgs'].length>0){
			var img = doc['imgs'][0];
			var ext = '.jpg';
			if (img.match('jpeg')){
		    	    ext = '';
		    	    img = encodeURIComponent(img);
		    	}
			retval = '/image/'+this.id+'/'+img+ext;
		    }
		    return retval;
		},
		previousCheaperBetter:{
		    1:'',
		    0:'',
		    dir:1
		},

		cheaperBetter:function(delta, cond, jump){
		    var th = this;
		    var storage = this.get('storage');
		    var sorted = storage.sort(function(doc1,doc2){
						  return doc1.price-doc2.price;
					      });
		    var in_sorted = _(sorted).map(function(doc){return doc._id;}).indexOf(th.id);
		    if (cond(in_sorted,sorted.length)){
			return undefined;
		    }
		    var new_index = in_sorted+delta;
		    if (jump)
			new_index+=jump;
		    var new_doc = sorted[new_index];
		    var component_id = new_doc['_id'];
		    if (this.previousCheaperBetter['dir'] == delta &&
		    	this.previousCheaperBetter[delta+1] == component_id){
		    	//this component was allready shown
		    	//we have infinite loop here
		    	return this.cheaperBetter(delta,cond, delta);
		    }

		    var old_component = this;
		    this.previousCheaperBetter[delta+1] = this.id;
		    this.previousCheaperBetter['dir'] = delta;
		    var collection = this.get('collection');
		    var new_component = new Component({
					     id:component_id,
							  part:old_component.get('part'),
							  alias:old_component.get('alias'),
							  count:old_component.get('count'),
							  storage:old_component.get('storage'),
							  collection:collection
					 });		    
		    collection.add(new_component);
		    collection.remove(this);		    
		    return new_component;
		}
	    });
var SateliteView = Backbone
    .View
    .extend({
		initialize:function(){
		    _.bindAll(this, "makeActive", "render", "getDescription");
		},
		events:{
		    click:"makeActive"
		},
		getDescription:function(component){
		    return this.options.parent.getDescription(component);
		},
		makeActive:function(){
		    var parent = this.options.parent;
		    //if switching socket, do not render central view for the component
		    //on the other side of socket

		    var old_central_view = parent.central_view;
		    var new_central_view = new CentralView({
							       model:this.model,
							       el:old_central_view.el,
							       id:this.model.get('alias'),
							       box_size:parent.central_box_size
							   });
		    new_central_view.render();
		    parent.central_view = new_central_view;


		    //remove old element
		    var old_active_view = parent.active_satelite;


		    if(old_active_view == this){
		    }
		    else{
			old_active_view.$el.remove();
		    }
		    // make ordinal view
		    if (old_active_view.model.get('alias')!==this.model.get('alias')){
			var ordinal_view = parent.makeSatelite(old_active_view.model,
							       old_active_view.options.clock);
			ordinal_view.render();
			parent.satelites = _(parent.satelites)
			    .select(function(v){
					return v.model.id!=old_active_view.model.id;});
			parent.satelites.push(ordinal_view);
		    }

		    parent.active_satelite = this;
		    this.active = true;
		    var th = this;
		    parent.satelites = _(parent.satelites)
			.select(function(v){
				    return v.model.id!==th.model.id;});
		    parent.satelites.push(this);


		    //increase this view
		    this.options.box_size = parent.active_satelite_size;
		    this.$el.attr('width',parent.active_satelite_size);
		    this.$el.attr('height',parent.active_satelite_size);
		    //shift active view according to its size
		    var delta = (parent.active_satelite_size-parent.satelite_box_size)/2;
		    var pos = this.$el.position();
		    this.$el.css({top:pos.top-delta+'px','left':pos.left-delta+'px'});
		    this.render();
		    this.options.box_size = this.options.box_size/2;
		    this.getDescription(this.model);

		},
		renderCycle:function(){
		    this.el.width = this.el.width;
		    var full_box_size = this.options.box_size;
		    var half_box_size = full_box_size / 2;
		    var context = this.el.getContext("2d");
		    var centerX = half_box_size;
		    var centerY = half_box_size;
		    var radius = half_box_size-3;

		    context.beginPath();
		    context.arc(centerX, centerY, radius, 0, 2 * Math.PI, false);

		    context.lineWidth = 5;
		    context.strokeStyle = "#B9D3E1";
		    context.stroke();
		    context.clip();
		    context.fillStyle = "white";
		    context.fill();
		    var model = this.model;
		    var image_src = model.getIcon();
		    if(image_src.match('no_image')){
			context.font = "10pt Calibri";
			context.fillStyle = "black";
			context.textAlign = "center";
			context.fillText(parts_names[parts_aliases[this.model.get('alias')]],
					 centerX, centerY);
			context.fillText('нет', centerX, centerY+10);
			context.fillText('картинки', centerX, centerY+20);
			return;
		    }

		    var imageObj = new Image();

		    imageObj.onload = function(){
			var to_scale = imageObj.width;
			var other = imageObj.height;
			if (imageObj.width>imageObj.height){
			    to_scale = imageObj.height;
			}
			var wratio = full_box_size/imageObj.width;
			var hratio = full_box_size/imageObj.height;
			var scale = wratio;
			if (wratio>hratio)
			    scale = hratio;
			if (-50 < imageObj.height-imageObj.height < 20)
			    scale = scale*0.9;
			var new_width = imageObj.width*scale;
			var new_height = imageObj.height*scale;
			var woffset = (full_box_size-new_width)/2;
			var hoffset = (full_box_size-new_height)/2;
			context.drawImage(imageObj, woffset, hoffset,
					  new_width,new_height);
		    };
		    imageObj.src = image_src;

		},
		render:function(){
		    this.renderCycle();
		}
	    });

var CentralView = SateliteView
    .extend({
	    });

var Model = Backbone
    .Collection
    .extend({
		model: Component,
		getByPart:function(part){
		    return this
			.chain()
			.select(function(c){return c.get('part')==part;})
			.first()
			.value();
		},
		getByAlias:function(alias){
		    return this
			.chain()
			.select(function(c){return c.get('alias')==alias;})
			.first()
			.value();
		}
	    });

var ModelView = Backbone
    .View
    .extend({
		initialize:function(){
		    _.bindAll(this, "makeSatelite",
			      "makeSateliteAttributes","makeBetter",
			      "makeCheaper", "cheaperBetter",
			      "fillDescription","getDescription",
			      "componentChanged", "save", "getCatalogs", "checkConfig",
			      "checkSocket");
		},
		events:{
		    'click #gcheaper':"makeCheaper",
		    'click #gbetter':"makeBetter",
		    'click #ctocart':"save",
		    'change #odvd':"recalculate",
		    'change #obuild':"recalculate",
		    'change #oinstalling':"recalculate"
		},
		getCatalogs:function(alias){
		    var m = this.collection.getByAlias(alias);
		    //???
		    // var doc = _(m.get('storage'))
		    // 	    .select(function(doc){return doc._id==m.id;})[0];
		    var doc = m.get('doc');
		    return doc['catalogs'];
		},
		save:function(){
		    var model_to_store = {};
		    var to_send = {};
		    var items = {};
		    var edit = false;//edit used when 'save' is click
		    this.collection.each(function(m){
					     var count = m.get('count');
					     var id = m.get('doc')._id;
					     if (count>1){
						 var new_id = [];
						 while (count!=0){
						     new_id.push(id);
						     count-=1;
						 }
						 id = new_id;
					     }
					     items[m.get('part')]=id;
					 });
		    model_to_store['items'] = items;
		    model_to_store['mother_catalogs'] = this.getCatalogs('mother');
		    model_to_store['proc_catalogs'] = this.getCatalogs('proc');

		    if (uuid){
		    	if (edit && !processing){
		    	    model_to_store['id'] = uuid;
		    	    to_send['edit'] = 't';
		    	}
		    	else{
		    	    model_to_store['parent'] = uuid;
		    	}
		    }
		    else{
		    	model_to_store['parent'] = _(document.location.href.split('/')).last().split('?')[0];
		    }
		    model_to_store['installing'] = this.$el.find('#oinstalling').is(':checked');
		    model_to_store['building'] = $('#obuild').is(':checked');
		    model_to_store['dvd'] = this.$el.find('#odvd').is(':checked');


		    to_send['model'] = JSON.stringify(model_to_store);
		    $.ajax({
		    	       url:'/save',
		    	       data:to_send,
		    	       success:this.to_cartSuccess
		    	   });
		},
		to_cartSuccess: function(data){
		    if (!data['id'])
			alert('Что то пошло не так :(');
		    else{
			uuid = data['id'];
			var cart_el = $('#cart');
			if (cart_el.length>0){
			    cart_el.text('Корзина('+$.cookie('pc_cart')+')');
			}
			else{
			    if (!data['edit']){
				$('#main_menu')
				    .append(_.template('<li><a id="cart" href="/cart/{{cart}}">Корзина(1)</a></li>',
						       {
							   cart:$.cookie('pc_user')
						       }));
			    }
			}
			alert('Получилось!');
		    }
		},
		cheaperBetter:function(delta, cond, jump){
		    var component = this.active_satelite.model;
		    var new_component = component.cheaperBetter(delta, cond, jump);
		    var clock = this.active_satelite.options.clock;
		    var new_satel_view = this.makeSatelite(new_component, clock);		    
		    new_satel_view.makeActive();
		    this.componentChanged(new_component, delta);
		    return new_component;
		},
		componentChanged:function(component, delta){
		    // during checkConfig other components possible will be changed
		    this.checkConfig(component, delta);
		    this.recalculate();
		    this.getDescription(component);
		},
		checkConfig:function(component, delta){
		    var alias = component.get('alias');
		    if (alias=='proc' || alias == 'mother'){
			var may_be_changed = this.checkSocket(component, delta);
		    }
		},
		checkSocket:function(component, delta){
		    var mother_catalogs = this.getCatalogs('mother');
		    var proc_catalogs = this.getCatalogs('proc');
		    var mapped = _(mother_to_proc_mapping)
			.select(function(mp){
				    var mother_map = mp[0];
				    var proc_map = mp[1];
				    return _.difference(mother_map, mother_catalogs).length==0
					&& _.difference(proc_map, proc_catalogs).length==0;
				});
		    if (mapped.length==0){
			//may be it need to change socket!
			//mark that socket is changed if needed.
			//socket must be changed only once
			//if user switch motherboard and it is not compatible with proc_catalogs
			//i will switch to proc now and make it cheaper or better
			//but during this switching DO NOT SWITCH BACK to mother!
			//change only proc for all other iterations
			var other;
			if (this.socketTransition){
			    //change the same component
			    other = component.get('alias');
			}
			else{
			    //change component on other side of socket
			    if (component.get('alias') == 'proc')
				other = 'mother';
			    else
				other = 'proc';
			    this.socketTransition = true;
			}
			var other_model = this.collection.getByAlias(other);
			var cond = function(index,length){return index-1<0;};
			var new_other_model = other_model
			    .cheaperBetter(delta,cond);
			if (!new_other_model)
			    new_other_model = other_model
			    .cheaperBetter(0-delta,cond);
			console.log(new_other_model);
			return new_other_model;
		    }
		    else{
			//all clear. change socket transition to initial
			this.socketTransition = false;
			return component;
		    }
		},
		getDescription:function(component){
		    this.$el.find('#cdescription').css('opacity',0);
		    $.ajax({url:'/component',data:{id:component.id},
			    success:this.fillDescription(component)});
		},
		fillDescription:function(component){
		    var descr = this.$el.find('#cdescription');
		    return function(data){
			descr.jScrollPaneRemove();
			descr.html('<h2>'+component.get('doc').text+'</h2>'+data['comments'])
		    	    .jScrollPane();
			descr.parent().css({'float':'right'}).css('top','40px');
			descr.animate({'opacity':'1.0'}, 300);
		    };
		},
		makeBetter:function(){
		    return this.cheaperBetter(1,function(index,length){return index+1>=length;});
		},
		makeCheaper:function(){
		    return this.cheaperBetter(-1,function(index,length){return index-1<0;});
		},
		recalculate:function(){
		    var price = this
			.collection.reduce(function(acc,model){
					       return acc+model.get('doc').price*model.get('count');
					   },0);
		    if(this.$el.find('#odvd').is(':checked')){
			price+=800;
		    }
		    if(this.$el.find('#obuild').is(':checked')){
			price+=800;
		    }
		    if(this.$el.find('#oinstalling').is(':checked')){
			price+=800;
		    }
		    var text_price = price+'';
		    if (text_price.length>=5){
			text_price = text_price.substr(0,2)+' '+text_price.substr(2,3);
		    }
		    this.$el.find('#cprice').text(text_price);
		},
		style_template:_.template("position:absolute;left:{{left}};top:{{top}};"),
		makeSateliteAttributes:function(box_size, x,y){
		    return {
			width:box_size,
			height:box_size,
			'class':'satelite',
			style:this.style_template({
						      left:x-box_size/2+'px',
						      top:y-box_size/2+'px'
						  })
		    };
		},
		makeSatelite:function(m,i){
		    var angle = this.satelite_angle*i;
		    //offset from central to center of satelite
		    var offset_x = this.satelite_radius*Math.cos(angle);
		    var offset_y = this.satelite_radius*Math.sin(angle);
		    var satel_x = offset_x+this.central_pos.left;
		    var satel_y = offset_y+this.central_pos.top;
		    var box_size = this.satelite_box_size;
		    var satel_view = new SateliteView({model:m,
						       tagName:'canvas',
						       attributes:this.makeSateliteAttributes(
							   box_size,
							   satel_x,
							   satel_y),
						       clock:i,
						       box_size:box_size,
						       parent:this
						      });
		    this.$el.append(satel_view.el);
		    this.satelites = _(this.satelites)
		    	.select(function(view){
		    		    return view.model.get('alias') !== m.get('alias');
		    		});
		    this.satelites.push(satel_view);
		    return satel_view;
		},
		render: function() {
		    var _case = this.collection.getByAlias('case');
		    this.central_view = new CentralView({
							    model:_case,
							    el:document.getElementById('ccenter'),
							    box_size:this.central_box_size
							});
		    //do not render it cause will render it during makeActive
		    //this.central_view.render();
		    this.central_pos = this.central_view.$el.position();
		    //move satelite little up
		    this.central_view.$el.css({'top':this.central_pos.top-30+'px'});
		    //add offset for surrounding satelites calculations (to find center)
		    this.central_pos.left+=this.central_view.options.box_size/2;
		    this.central_pos.top+=this.central_view.options.box_size/2;
		    //make case default active view
		    this.collection.map(this.makeSatelite);
		    _(this.satelites).each(function(view){
					       if (view.model.get('alias')!='case')
						   view.render();
					   });
		    var case_view = _(this.satelites)
			.select(function(view){
				    return view.model.get('alias')=='case';})[0];
		    //this is a hack. i do not have active view yet, but it is required by makeActive
		    this.active_satelite = case_view;
		    case_view.makeActive({});
		    this.central_view.$el.after('<div id="gbetter" class="large_button"></div>');
		    this.central_view.$el.next().css({
							 position:'absolute',
							 top:'535px',
							 left:'600px',
							 'float':'none',
							 margin:0
						     });
		    this.central_view.$el.after('<div id="gcheaper" class="large_button"></div>');
		    this.central_view.$el.next().css({
							 position:'absolute',
							 top:'535px',
							 left:'545px',
							 'float':'none',
							 margin:0
						     });
		    this.componentChanged(_case, 1);
		},
		central_box_size:300,
		satelite_radius:250,
		satelite_angle:2*Math.PI/12,
		satelite_box_size:88,
		active_satelite_size:136,
		code:function(){
		    return this.central_view.model.id;
		}
	    });

var model_view;

(function init(){
     var aliases_reverted = {};
     _(parts_aliases).chain().keys().each(function(key){aliases_reverted[parts_aliases[key]]=key;});
     var model_components = _(model['items'])
	 .chain()
	 .keys()
	 .map(function(key){
		  var alias = aliases_reverted[key];
		  var component_id = model['items'][key];
		  var count = 1;
		  //hack. this means it is list! everery string id is more than 4 by default
		  if (component_id.length<=4){
		      count = component_id.length;
		      component_id = component_id[0];
		  }
		  var c = new Component({
					    id:component_id,
					    part:key,
					    alias:aliases_reverted[key],
					    count:count,
					    storage:choices[key]
					});
		  return c;
	      })
	 .value();
     var model_collection = new Model(model_components);
     model_collection.each(function(m){m.set({collection:model_collection});});
     model_view = new ModelView({
				    collection:model_collection,
				    el:document.getElementById('ccontainer')
				});
     model_view.render();

 })();
