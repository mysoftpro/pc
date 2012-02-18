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
                    if (img){
                        var ext = '.jpg';
                        if (img.match('jpeg')){
                            ext = '';
                            img = encodeURIComponent(path);
                        }
                    }
                    return '/image/'+this.id+'/'+img+ext;
                }
            });
var SateliteView = Backbone
    .View
    .extend({
		initialize:function(){
		  _.bindAll(this, "getStyle");
		},
                box_size:88,
                style_template:_.template("position:absolute;left:{{left}};top:{{top}};border:1px solid red"),
                getStyle:function(){
                    return this.style_template({
                                                   left:this.options.x-this.box_size/2+'px',
                                                   top:this.options.y-this.box_size/2+'px'
                                               });
                },
                renderCycle:function(){
                    var context = this.el.getContext("2d");
                    var centerX = this.box_size / 2;
                    var centerY = this.box_size  / 2;
                    var radius = (this.box_size-3)/2;

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
                        context.drawImage(imageObj, 0, 0, 235,235);
                    };
                    imageObj.src = this.model.getIcon();

                },
                render:function(){
                    this.renderCycle();
                }
            });

var CentralView = SateliteView
    .extend({
                box_size:235
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
                    _.bindAll(this, "renderSatelite");
                },
                events: {
                },
                renderSatelite:function(m,i){
                    var angle = this.satelite_angle*i;
                    //offset from central to center of satelite
                    var offset_x = this.satelite_radius*Math.cos(angle);
                    var offset_y = this.satelite_radius*Math.sin(angle);
                    var satelite_center_x = offset_x+this.central_pos.left;
                    var satelite_center_y = offset_y+this.central_pos.top;
                    var satel_view = new SateliteView({x:satelite_center_x, y:satelite_center_y});

                    this.$el
                        .append(satel_view
                                .make('canvas',
                                      {width:satel_view.box_size,
                                       'height':satel_view.box_size,
                                       'style':satel_view.getStyle()
                                      }));
		},
                render: function() {
                    var _case = this.collection.getByAlias('case');
                    var case_view = new CentralView({
                                                    model:_case,
                                                    el:document.getElementById('ccenter')
                                                });
                    case_view.render();
                    this.central_pos = case_view.$el.position();
                    this.central_pos.left+=case_view.box_size/2;
                    this.central_pos.top+=case_view.box_size/2;
                    this
                        .collection
                        .each(this.renderSatelite);
                },
                satelite_radius:255,
                satelite_angle:2*Math.PI/12,
                satelite_box_size:88
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
