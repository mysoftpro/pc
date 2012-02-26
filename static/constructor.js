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
		    this.set('doc',
			     _(storage)
			     .chain()
			     .select(function(doc){
					 return doc['_id']==id;})
			     .first()
			     .value());
		},
		dget:function(ob,key,_def){
		    var def = {};
		    if (_def)
			def = _def;
		    if (ob[key])
			return ob[key];
		    return def;
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
		}
	    });
var SateliteView = Backbone
    .View
    .extend({
		initialize:function(){
		    _.bindAll(this, "makeActive", "render");
		},
		events:{
		    click:"makeActive"
		},
		makeActive:function(){
		    var parent = this.options.parent;
		    var old_central_view = parent.central_view;
		    var new_central_view = new CentralView({
							      model:this.model,
							      el:old_central_view.el,
							      id:this.model.get('alias'),
							      box_size:parent.central_box_size
							});
		    new_central_view.render();
		    parent.central_view = new_central_view;
		    //ttt
		    var old_active_view = parent.active_satelite;
		    if (old_active_view.model.get('alias')!==this.model.get('alias')){
			old_active_view.$el.remove();
			var ordinal_view = parent.makeSatelite(old_active_view.model,
							       old_active_view.options.clock);
			ordinal_view.render();
		    }


		    var delta = (parent.active_satelite_size-parent.satelite_box_size)/2;

		    //reduce old active view
		    parent.active_satelite.options.box_size = parent.satelite_box_size;
		    parent.active_satelite.$el.attr('width',parent.satelite_box_size);
		    parent.active_satelite.$el.attr('height',parent.satelite_box_size);
		    // shift
		    var apos = parent.active_satelite.$el.position();
		    parent.active_satelite.$el.css({top:apos.top+delta+'px',
						    'left':apos.left+delta+'px'});

		    // ttt
		    parent.active_satelite = this;
		    this.active = true;

		    //increase this view
		    this.options.box_size = parent.active_satelite_size;
		    this.$el.attr('width',parent.active_satelite_size);
		    this.$el.attr('height',parent.active_satelite_size);
		    // shift
		    var pos = this.$el.position();
		    this.$el.css({top:pos.top-delta+'px','left':pos.left-delta+'px'});
		    this.render();
		    this.options.box_size = this.options.box_size/2;
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
		    imageObj.src = this.model.getIcon();

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
			     "fillDescription");
		},
		events:{
		    'click #gcheaper':"makeCheaper",
		    'click #gbetter':"makeBetter"
		},
		previousCheaperBetter:{
		    1:'',
		    0:'',
		    dir:1
		},
		cheaperBetter:function(delta, cond, jump){
		    var model = this.active_satelite.model;
		    var storage = model.get('storage');
		    var sorted = storage.sort(function(doc1,doc2){
						  return doc1.price-doc2.price;
					      });
		    var in_sorted = _(sorted).map(function(doc){return doc._id;}).indexOf(model.id);
		    if (cond(in_sorted,sorted.length)){
			return;
		    }
		    var new_index = in_sorted+delta;
		    if (jump)
			new_index+=jump;
		    var new_doc = sorted[new_index];
		    var count = 1;
		    var component_id = new_doc['_id'];
		    //hack
		    if (component_id.length<=2){
			count = component_id.length;
			component_id = component_id[0];
		    }
		    if (this.previousCheaperBetter['dir'] == delta &&
		    	this.previousCheaperBetter[delta+1] == component_id){
		    	//this component was allready shown
		    	//we have infinite loop here
		    	return this.cheaperBetter(delta,cond, delta);
		    }
		    var clock = this.active_satelite.options.clock;
		    var old_component = this.active_satelite.model;
		    this.previousCheaperBetter[delta+1] = old_component.id;
		    this.previousCheaperBetter['dir'] = delta;
		    var new_component = new Component({
						      id:component_id,
						      part:old_component.get('part'),
						      alias:old_component.get('alias'),
						      count:count,
						      storage:old_component.get('storage')
						  });
		    //this.active_satelite.$el.remove();
		    var new_satel_view = this.makeSatelite(new_component, clock);
		    this.collection.remove(old_component);
		    this.collection.add(new_component);
		    new_satel_view.makeActive();
		    this.componentChanged(component_id);
		},
		componentChanged:function(component_id){
		    this.recalculate();
		    this.$el.find('#cdescription').css('opacity',0);
		    $.ajax({url:'/component',data:{id:component_id},success:this.fillDescription});
		},
		fillDescription:function(data){
		    var descr = this.$el.find('#cdescription');
		    descr.jScrollPaneRemove();
		    descr.html(data['comments'])
		    	.jScrollPane();
		    descr.parent().css({'float':'right'}).css('top','40px');
		    descr.animate({'opacity':'1.0'}, 300);
		},
		makeBetter:function(){
		    this.cheaperBetter(1,function(index,length){return index+1==length;});
		},
		makeCheaper:function(){
		    this.cheaperBetter(-1,function(index,length){return index-1<=0;});
		},
		recalculate:function(){
		    var price = this
			.collection.reduce(function(acc,model){
					       return acc+model.get('doc').price;},0);
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
		    var satelites = this
			.collection
			.map(this.makeSatelite);
		    _(satelites).each(function(view){
					  if (view.model.get('alias')!='case')
					      view.render();
				      });
		    var case_view = _(satelites)
			.select(function(view){
				    return view.model.get('alias')=='case';})[0];
		    //this is a hack. i do not have active view yet, but it is required by makeActive
		    this.active_satelite = case_view;
		    case_view.makeActive();
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
		    this.componentChanged(_case.id);
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
		  //hack
		  if (component_id.length<=2){
		      count = component_id.length;
		      component_id = component_id[0];
		  }
		  return new Component({
					   id:component_id,
					   part:key,
					   alias:aliases_reverted[key],
					   count:count,
					   storage:choices[key]
				       });
	      })
	 .value();
     var model_collection = new Model(model_components);
     model_view = new ModelView({
					collection:model_collection,
					el:document.getElementById('ccontainer')
				    });
     model_view.render();

 })();
