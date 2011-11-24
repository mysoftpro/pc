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

















var ajax = {
   "_id": "ajax",
   "_rev": "47-14adef9a01bff8f9f1ef6374a37685cd",
   "name": "Аякс",
   "link_to_dual_graphics": "http://www.amd.com/us/products/technologies/dual-graphics/pages/dual-graphics.aspx#3",
   "components": [
       {
	   "type": "case",
	   "code": "19208",
	   "name": "Корпус Delux DLC-MQ827",
	   "original_price": 40,
	   "order": 10,
	   "top_image": "deluxe.png",
	   "bottom_images": [
	       "eyefinity.png",
	       "appaceleration.png"
	   ],
	   "description": "Отличный корпус, покрашенный снуружи и изнутри.Продуманная аэродинамика для повышенного охлаждения и шумоподавления. Блок питания 600W чтобы заранее покрыть все возможные потребности ваших usb устройств и видеоконтроллеров."
       },
       {
	   "type": "mother",
	   "code": "19992",
	   "name": "Материнская плата GIGABYTE GA-A55M-S2V",
	   "original_price": 74,
	   "order": 20,
	   "top_image": "deluxe.png",
	   "description": "Новейшая материнская плата поддерживает технологию CrossFire, так что вы сможете добавить в систему вторую видеокарту и генерировать картинку двумя видеокартами параллельно. 6 каналов Sata и встроенный raid контроллер. Технологии понижения шума и энергопотребления."
       },
       {
	   "type": "proc",
	   "code": "20017",
	   "name": "Процессор AMD A4 X2 3300 2,5 ГГц",
	   "original_price": 78,
	   "order": 30,
	   "top_image": "deluxe.png",
	   "description": "Новейший процессор A4-3300 помимо двух ядер имеет встроенное видеоядро, которое работает в параллель с видеокартой по технологии AMD Dual Graphics."
       },
       {
	   "type": "video",
	   "name": "HD6450 XFX 1GB DDR3 DVI+VGA+HDMI BOX HD-645X-ZNH2",
	   "code": "19470",
	   "original_price": 53,
	   "order": 40,
	   "top_image": "hd6450.png",
	   "description": "Чипсет HD6450 поддерживает технологии AMD HD3D Technology, AMD Accelerated Parallel Processing Technology, AMD PowerPlay TechnologyAMD Eyefinity Technology Позволяет подключать до 5 дисплеев. Полная аппаратная поддержка DirectX® 11. Возможность добавить вторую карту и работатать параллельно с технологией CrossFire. Работает параллеьно с APU серии A по технологии AMD Dual Graphics."
       },
       {
	   "type": "hdd",
	   "name": "Жесткий диск 1000GB WD GreenPower Sata2 64mb WD10EARS",
	   "code": "15318",
	   "original_price": 125,
	   "order": 40,
	   "top_image": "deluxe.png",
	   "description": "Жесткий диск Western Digital - лучшее предложение на рынке."
       },
       {
	   "type": "ram",
	   "name": "ОЗУ 2X DDR3 4096MB Crucial Rendition CL9 1333 PC3-10600",
	   "code": "19575",
	   "original_price": 46,
	   "order": 40,
	   "top_image": "deluxe.png",
	   "description": "Память"
       },
       {
	   "type": "audio",
	   "name": "Акустическая система Genius SW-M2.1 350, 11W black",
	   "code": "18692",
	   "original_price": 17,
	   "order": 40,
	   "top_image": "deluxe.png",
	   "description": "Audio"
       },
       {
	   "type": "dvd",
	   "name": "Дисковод DVD-RW Samsung SH-222AB/BEBE Sata",
	   "code": "18932",
	   "original_price": 25,
	   "order": 40,
	   "top_image": "deluxe.png",
	   "description": "Dvd"
       },
       {
	   "type": "display",
	   "name": "Монитор LED BenQ GL2240 21.5\"/5ms/250",
	   "code": "17705",
	   "original_price": 147,
	   "order": 40,
	   "top_image": "deluxe.png",
	   "description": "Display"
       },
       {
	   "type": "windows",
	   "name": "ПО Microsoft Win 7 Home Basic 64-bit Rus CIS SP1",
	   "code": "17398",
	   "original_price": 72,
	   "order": 40,
	   "top_image": "deluxe.png",
	   "description": "Windows"
       }
   ],
   "_attachments": {
       "hd6450.png": {
	   "content_type": "image/png",
	   "revpos": 44,
	   "digest": "md5-rNvob351sp+CNaMsGpfRug==",
	   "length": 98431,
	   "stub": true
       },
       "appaceleration.png": {
	   "content_type": "image/png",
	   "revpos": 23,
	   "digest": "md5-CfrCiOo04AkqYPx+WbKXLQ==",
	   "length": 56024,
	   "stub": true
       },
       "eyefinity.png": {
	   "content_type": "image/png",
	   "revpos": 18,
	   "digest": "md5-818amsDJSskXvaFok2VSUQ==",
	   "length": 37193,
	   "stub": true
       },
       "deluxe.png": {
	   "content_type": "image/png",
	   "revpos": 16,
	   "digest": "md5-fmk1GNISFmJWIr3ZhESSZg==",
	   "length": 32051,
	   "stub": true
       }
   }
}