$(function(){
    $('#tips').click(function(e){			
			 e.preventDefault();
			 guider.createGuider({
						attachTo: "#mother",
						description: "Список доступных компонентов откроется после повторного клика. Описание компонента смотрите ниже на странице.",
						id: "list",
						position: 6,
						width: 160
					    }).show();

			guider.createGuider({
						attachTo: "#proc .body",
						description: "Название выбранного компонента",
						id: "body",
						position: 7,
						width: 100
					    }).show();

			guider.createGuider({
						attachTo: "#mother .cheaper",
						description: "Можно менять компоненты не открывая список.",
						id: "cheaperBetter",
						position: 6,
						width: 130
					    }).show();

			guider.createGuider({
						attachTo: "#owindows",
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
guider.createGuider({
						attachTo: "#baseprice",
						description: "Цена и индекс производительности до ваших именений.",
						id: "baseprice",
						position: 6,
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
      }
      $('.inactive').click(swapTabs);
});