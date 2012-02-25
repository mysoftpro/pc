function(doc) {
    var exceptions =["гарантия","кредит","доставка","руб....","возможно","недорого","гарантией.","состоянии","модель","большой","коробочке","полностью","гарантией","леонова","недорого.","продается","срочно","хорошая","хорошее", "москве"];
    if (doc.phone &&
	(doc.phone !== '') &&
        (doc.phone !== '89022506126' &&
	 doc.phone !== '+79210095968'&&
	doc.phone !== '76-10-24'&&
	doc.phone !== '8-911-471-66-31' &&
	doc.phone !== '89097800424'&&
	doc.phone !== '89114526397'&&
	doc.phone !== '89114590742'&&
	doc.phone !== '89114631553'&&
	doc.phone !== '89114894666'&&
	doc.phone !== '89114958717'&&
	doc.phone !== '89118559663'&&
	doc.phone !== '89216030781'&&
	doc.phone !== '89218525433'&&
	doc.phone !== '89506757505'&&
	doc.phone !== '89637385262'&&
	doc.phone !== '89814508151'&&
	doc.phone !== '992338'&&
	doc.phone !== 'Отправить e-mail'&&
	doc.phone !== '+79118620941'&&
	doc.phone !== '+79814587585'&&
	doc.phone !== '777-456'&&
	doc.phone !== '56-32-65'&&
	doc.phone !== 'Интернет-магазин http://max-price.ru/Отправить e-mail'&&
	doc.phone !== '+7-967-1186367'&&
	doc.phone !== '790-36-98'&&
	doc.phone !== '8 925 206 35 31'&&
	doc.phone !== '8 926 031 81 81'&&
	doc.phone !== '8-905-513-0658'&&
	doc.phone !== '8-905-734-63-83'&&
	doc.phone !== '8-910-456-8678'&&
	doc.phone !== '8-926-265-42-75'&&
	doc.phone !== '8-926-316-0763'&&
	doc.phone !== '8-965-284-14-50'&&
	doc.phone !== '8909 9836744'&&
	doc.phone !== '8909-620-5184'&&
	doc.phone !== '8929 576 03 00'&&
	doc.phone !== '8965-284-14-50'&&
	doc.phone !== '949-91-53'&&
	doc.phone !== '9499153'&&
	doc.phone !== '89506782708'&&
	 doc.phone !== '37 30 99'&&
	 doc.phone !== '89527978731'&&
	doc.phone !== '509787'
	) &&
	doc.phone.match(/\d+/g) &&
        doc.price && doc.price !=='' &&
        doc.date  &&
        doc.subj){
	var splitted = doc.subj.toLowerCase()
	    .replace('продам', '')
	    .replace('продаю', '')
	    .replace('Куплю', '')
	    .replace(/\,/g, '')
	    .replace(/\(/g, ' ')
	    .replace(/\)/g, '')
	    .split(' ');
	
	for (var i=0,l=splitted.length;i<l;i++){
	    var to_emit = splitted[i];
	    if (exceptions.indexOf(to_emit)>0)continue;
	    if (to_emit.length<=5)continue;
	    if (to_emit.charCodeAt(0)<=256)continue;
	    //.substring(0,to_emit.length-3)
	    emit(to_emit);
	}
            
    }
}