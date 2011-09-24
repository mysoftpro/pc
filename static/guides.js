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

    if ($.browser.msie && $.browser.version < 9){
        $('#' + container_id).corner('10px');
        $('#' + button_id).corner('6px');
    }
};

$(function(){
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



      function swapTabs(e){
	  var active = $('.active');
	  var target = $(e.target);
	  var klass = target.attr('class');
	  target.attr('class', active.attr('class'));
	  active.attr('class', klass);
	  target.unbind('click');
	  active.click(swapTabs);

	  var sign = '+=';
	  if (target.attr('id') == 'ourcomments')
	      sign = '-=';
	  var container = $('#descriptions');
	  container.data('jScrollPanePosition', 0);
	  container.css('top','0');
	  $('.description').animate({'margin-left':sign + 912}, 400);

      }
      $('.inactive').click(swapTabs);
      var ours = $('.our');
      for (var i=0,l=ours.length;i<l;i++){
	  var o = $(ours.get(i));
	  o.html(o.text());
      }      
});