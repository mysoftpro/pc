function (key, values, rereduce) {
    var retval = values.length;
    if (rereduce){
	retval = 0;
	for(var i=0;i<values.length;i++)
	    retval +=values[i];
    }
    return retval;
}