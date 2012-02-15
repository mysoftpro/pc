function(doc){
    if (doc.phone &&
	doc.phone !== '' &&
	doc.phone !== '89022506126' &&
	doc.phone !== '+79210095968' &&
	doc.phone !== '76-10-24' &&
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
	doc.phone !== 'Интернет-магазин http://max-price.ru/Отправить e-mail'
       ){
	emit(doc['phone']);
    }
}