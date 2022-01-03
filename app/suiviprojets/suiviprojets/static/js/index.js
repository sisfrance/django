$(function(){
	var calendar = new FullCalendar.Calendar(document.getElementById("calendar"),{height:500,
																				contentHeight:110,
																				aspectRatio:0.5,
																				expandRows:true,
																				eventSources:[eventscp,eventsct,eventsce],
																				initialView:'dayGridMonth',
																				eventContent:function(arg){
																						let statut_marker=document.createElement("span");
																						statut_marker.setAttribute("class","statut");
																						console.log(arg.event.extendedProps);
																						statut_marker.setAttribute("style","background-color:#"+arg.event.extendedProps.statut+";");
																						let content=document.createElement("p");
																						content.innerHTML=arg.event.title;
																						let arrayofDomNodes=[statut_marker,content];
																						return {domNodes:arrayofDomNodes};
																					
																				}
																				});
	calendar.render();
});
