$(function(){
	var calendar = new FullCalendar.Calendar(document.getElementById("calendar"),{height:500,
																				contentHeight:110,
																				aspectRatio:0.5,
																				expandRows:true,
																				eventSources:[eventsct,eventscp],
																				initialView:'dayGridMonth'});
	calendar.render();
});
