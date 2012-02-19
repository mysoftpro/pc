_.templateSettings = {
    interpolate : /\{\{(.+?)\}\}/g
    ,evaluate: /\[\[(.+?)\]\]/g
};

var Component = Backbone
    .Model
    .extend({
                initialize:function(){
                    this.set('doc', this.getObjectFromStorage());
                },
                getObjectFromStorage:function(){
                    var _id = this.id;
                    var storage = this.get('storage');
                    if (storage['rows'])
                        return _(storage['rows']).chain()
                        .select(function(ob){
                                    return ob.doc._id == _id;
                                })
                        .first()
                        .value()
                        .doc;
                    return _(this.get('storage'))
                        .chain()
                        .values()
                        .map(function(arr){return arr[1];})
                        .map(function(ob){
                                 return ob[1]['rows'];
                             })
                        .map(function(arr){
                                    return _(arr).select(function(ob){
                                                             return ob.doc._id == _id;
                                                         });
                              })
                        .map(function(some){return some;})
                        .select(function(arr){return arr.length>0;})
                        .first()
                        .first()
                        .value()
                        .doc;
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
                    var img = this.dget(this.dget(this.get('doc'),'description'),'imgs',[])[0];
                    var ext = '.jpg';
                    if (img){
                        if (img.match('jpeg')){
                            ext = '';
                            img = encodeURIComponent(img);
                        }
                    }
                    else{
                        return '/static/no_image.jpg';
                    }
                    return '/image/'+this.id+'/'+img+ext;
                }
            });
var SateliteView = Backbone
    .View
    .extend({
                initialize:function(){
                    _.bindAll(this, "makeActive");
                },
                events:{
                    click:"makeActive"
                },
                makeActive:function(){
                    var parent = this.options.parent;
                    var old_center_view = parent.central_view;
                    var new_center_view = new CentralView({
                                                              model:this.model,
                                                              el:old_center_view.el,
                                                              id:this.model.get('alias'),
                                                              box_size:parent.central_box_size
                                                        });
                    new_center_view.render();
                    parent.central_view = new_center_view;

                    var delta = (parent.active_satelite_size-parent.satelite_box_size)/2;

		    //reduce old active view
                    parent.active_satelite.options.box_size = parent.satelite_box_size;
		    parent.active_satelite.$el.attr('width',parent.satelite_box_size);
		    parent.active_satelite.$el.attr('height',parent.satelite_box_size);
		    // shift
		    var apos = parent.active_satelite.$el.position();		    		    
		    parent.active_satelite.$el.css({top:apos.top+delta+'px',
						    'left':apos.left+delta+'px'});
                    parent.active_satelite.render();

                    parent.active_satelite = this;

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
                    var half_box_size = this.options.box_size  / 2;
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

                    var imageObj = new Image();

                    imageObj.onload = function(){

                        var jimg = $(imageObj);
                        jimg.css('width','100px');
                        context.drawImage(imageObj, 0, 0, half_box_size*2,half_box_size*2);
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
                    _.bindAll(this, "renderSatelite",
                              "renderSatelite",
                              "makeSateliteAttributes");
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
                renderSatelite:function(m,i){
                    var angle = this.satelite_angle*i;
                    //offset from central to center of satelite
                    var offset_x = this.satelite_radius*Math.cos(angle);
                    var offset_y = this.satelite_radius*Math.sin(angle);
                    var satel_x = offset_x+this.central_pos.left;
                    var satel_y = offset_y+this.central_pos.top;
                    var box_size = this.satelite_box_size;
                    var active = false;
                    if (m.get('alias') == 'proc'){
                        box_size = this.active_satelite_size;
                        active = true;
                    }
                    var satel_view = new SateliteView({model:m,
                                                       tagName:'canvas',
                                                       attributes:this.makeSateliteAttributes(
                                                           box_size,
                                                           satel_x,
                                                           satel_y),
                                                       x:satel_x,
                                                       y:satel_y,
                                                       active:active,
                                                       box_size:box_size,
                                                       parent:this
                                                      });
                    if (active)
                        this.active_satelite = satel_view;
                    this.$el.append(satel_view.el);
                    satel_view.render();
                },
                render: function() {
                    var _case = this.collection.getByAlias('case');
                    this.central_view = new CentralView({
                                                        model:_case,
                                                        el:document.getElementById('ccenter'),
                                                        box_size:this.central_box_size
                                                });
                    this.central_view.render();
                    this.central_pos = this.central_view.$el.position();
                    this.central_pos.left+=this.central_view.options.box_size/2;
                    this.central_pos.top+=this.central_view.options.box_size/2;
                    this
                        .collection
                        .each(this.renderSatelite);
                },
                central_box_size:235,
                satelite_radius:255,
                satelite_angle:2*Math.PI/12,
                satelite_box_size:88,
                active_satelite_size:136
            });


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
     var model_view = new ModelView({
                                        collection:model_collection,
                                        el:document.getElementById('ccontainer')
                                    });
     model_view.render();

 })();
