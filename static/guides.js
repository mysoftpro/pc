var filled_selects_helps = {    
};

var showYa = function (_id, _link){
    new Ya.share({
                     element: _id,
                     elementStyle: {
                         'type': 'none',
                         'border': false,
                         'quickServices': ['vkontakte', 'odnoklassniki','facebook','twitter','lj','moimir','moikrug','liveinternet']
                     },
                     link:_link,
                     title: 'buildpc.ru Просто купить компьютер',
                     serviceSpecific: {
                         twitter: {
                             title: 'buildpc.ru Просто купить компьютер'
                         }
                     }
                 });
};

$(function()
  {
      $('#tips').click(function(e){
                           e.preventDefault();
                           guider.createGuider({
                                                   attachTo: "#7388",
                                                   description: "Список доступных компонентов откроется после повторного клика. Описание компонента смотрите ниже на странице.",
                                                   id: "mother",
                                                   position: 6,
                                                   width: 160
                                               }).show();

                           guider.createGuider({
                                                   attachTo: "#7399 .body",
                                                   description: "Название выбранного компонента",
                                                   id: "body",
                                                   position: 7,
                                                   width: 100
                                               }).show();

                           guider.createGuider({
                                                   attachTo: "#7388 .cheaper",
                                                   description: "Можно менять компоненты не открывая список.",
                                                   id: "cheaperBetter",
                                                   position: 6,
                                                   width: 130
                                               }).show();

                           guider.createGuider({
                                                   attachTo: "#osoft",
                                                   description: "Некоторые опции можно отключить совсем.",
                                                   id: "options",
                                                   position: 6,
                                                   width: 130
                                               }).show();


                           guider.createGuider({
                                                   attachTo: "#gbetter",
                                                   description: "Эти кнопки позволяют изменять компоненты по алгоритму, который особое внимание уделяет производительности компьютера.",
                                                   id: "GCheaperGBetter",
                                                   position: 7,
                                                   width: 140
                                               }).show();

                           guider.createGuider({
                                                   attachTo: "#component_title",
                                                   description: "На этой вкладке описание компонента от поставщика.",
                                                   id: "descritpion",
                                                   position: 11,
                                                   width: 300
                                               }).show();

                           guider.createGuider({
                                                   attachTo: "#ourcomments",
                                                   description: "На этой вкладке наши комментарии по выбору компонента.",
                                                   id: "ourcomments",
                                                   position: 3,
                                                   width: 160
                                               }).show();

                           guider.createGuider({
                                                   attachTo: "#large_price",
                                                   description: "Текущая цена и индекс производительности",
                                                   id: "largeprice",
                                                   position: 9,
                                                   width: 160
                                               }).show();

                           $('body').click(function(e){
                                               if ($(e.target).attr('id') == 'tips')return;
                                               guider.hideAll();
                                           });
                       });

      function fillSelectHelps(action){
	  if (fillSelectHelps[current_row])
	      return action();
	  $.ajax({
                     url:'/select_helps/sh-'+current_row,
		     dataType: 'json',
                     success:function(data){					    
                         var row_index;
                         var trs = $('.component_viewlet');
                         for (var i=0;i<trs.length;i++){
                             if (trs.get(i).id==current_row){
				 var our = $($('.our').get(i));
                                 our.html(data.text);
				 fillSelectHelps[current_row] = true;
                                 break;
                             }
                         }
                         action();
                     },
                     error:function(){
			 fillSelectHelps[current_row] = true;
                         action();
                     }
                 });
      }
      
      function swapTabs(e){
          var active = $('.active');
          var target = $(e.target);
          var klass = target.attr('class');
          target.attr('class', active.attr('class'));
          active.attr('class', klass);
          target.unbind('click');
          active.click(swapTabs);

          if (target.attr('id') == 'ourcomments'){
              var container = $('#descriptions');
              container.data('jScrollPanePosition', 0);
              container.css('top','0');
              function animate(){
                  $('.description')
                      .animate({'margin-left':'-=912'}, 400);
              }
	      fillSelectHelps(animate);                      
          }
          else
              $('.description').animate({'margin-left':'+=912'}, 400);
      }
      $('.inactive').click(swapTabs);
      $('.body').click(function(){fillSelectHelps(function(){});});
  });