var Component = Backbone
    .Model
    .extend({

            });
var Model = Backbone
    .Collection
    .extend({
                model: Component
            });

var ModelView = Backbone.View.extend({
  events: {
  },
  render: function() {
  }
});


var central_box_size = 235;
var satelite_box_size = 88;
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
                                           count:count,
                                           alias:aliases_reverted[key],
                                           part:key,
                                           storage:choices[key]
                                       });
              })
         .value();
     var model_collection = new Model(model_components);

     // var model = new Model()
     // var container = $('#ccontainer');
     // var central = $("#ccenter");
     // var context = central[0].getContext("2d");
     // var centerX = central_box_size / 2;
     // var centerY = central_box_size  / 2;
     // var radius = (central_box_size-3)/2;

     // context.beginPath();
     // context.arc(centerX, centerY, radius, 0, 2 * Math.PI, false);

     // context.lineWidth = 5;
     // context.strokeStyle = "#B9D3E1";
     // context.stroke();
     // context.clip();

     // var imageObj = new Image();

     // imageObj.onload = function(){

     //     var jimg = $(imageObj);
     //     jimg.css('width','100px');
     //     context.drawImage(imageObj, 0, 0, 235,235);
     // };
     // imageObj.src = "image/new_109653/haf.jpg";

     // var component_ids = ['case','ram','proc','mother','video','hdd','psu','mouse',
     //                      'keyboard','os', 'dosplay','audio'];
     // var satelite_angle = (2*Math.PI/12);
     // var central_pos = central.position();
     // central_pos.left+=centerX;
     // central_pos.top+=centerY;
     // var satelite_radius = 255;
     // _(component_ids).each(function(c,i){
     //                           var angle = satelite_angle*i;
     //                           //offset from central to center of satelite
     //                           var offset_x = satelite_radius*Math.cos(angle);
     //                           var offset_y = satelite_radius*Math.sin(angle);
     //                           var satelite_center_x = offset_x+central_pos.left;
     //                           var satelite_center_y = offset_y+central_pos.top;
     //                           var satel = $(document.createElement('canvas'));
     //                           satel.attr('width',satelite_box_size);
     //                           satel.attr('height',satelite_box_size);
     //                           satel.attr('id', c);
     //                           satel.css({
     //                                         position:'absolute',
     //                                         left:satelite_center_x-satelite_box_size/2+'px',
     //                                         top:satelite_center_y-satelite_box_size/2+'px',
     //                                         border:'1px solid red'
     //                                     });
     //                           container.append(satel);
     //                           // container.append('<div>'+i+'</div>');
     //                       });
 })();