function toggle_maximize(element)
{
  var content = document.getElementById('foot');
  var image = document.getElementById('toggle');
  if (image.className == 'infotext_toggle_on') {
	alert('yeah');
	image.className = 'infotext_toggle_off';
	return 1;
  }
  if (image.className == 'infotext_toggle_off') {
	alert('yeah2');
	image.className = 'infotext_toggle_on';
	return 1;
  }
}