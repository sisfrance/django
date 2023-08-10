
$(function () {
	
	/****
	  * 6-TIMELINE
	  * **/
	 $("#myTimeline").Timeline({
	
	  // "bar" or "point"
	  type            : "bar",
	
	  // "years" or "months" or "days"
	  scale           : "months", 
	
	  // start <a href="https://www.jqueryscript.net/time-clock/">date</a> time
	  startDatetime   : "2023-01-01",
	
	  // end date time
	  endDatetime     : "auto",
	
	  // displays headline
	  headline        : {
	    display     : true,
	    title       : "",
	    range       : true,
	    locale      : "en-US",
	    format      : { hour12: false }
	  }, 
	
	  // displays sidebar
	  sidebar         : {
	    sticky      : false,
	    overlay     : false,
	    list        : [], //  an array of items
	  },
	
	  // displays ruler
	  ruler           : {
	    top         : {
	      lines      : ['year','month'],
	      height     : 30,
	      fontSize   : 14,
	      color      : "#777777",
	      background : "#FFFFFF",
	      locale     : "en-US",
	      format     : { hour12: false,
						year:'numeric',
						month:'long',
						}
	    },
	  },
	
	  // displays footer
	  footer          : {
	    display     : false,
	    content     : "",
	    range       : false,
	    locale      : "en-US",
	    format      : { hour12: false }
	  },
	
	  // displays event meta
	  eventMeta       : {
	    display     : false,
	    scale       : "day",
	    locale      : "en-US",
	    format      : { hour12: false },
	    content     : ""
	  },
	
	  // event data
	  eventData       : [],
	
	  // enables/disables effects
	  effects         : {
	    presentTime : true,
	    hoverEvent  : true,
	    stripedGridRow : true,
	    horizontalGridStyle : 'dotted',
	    verticalGridStyle : 'solid',
	  },
	
	  colorScheme     : { // Added new option since v2.0.0
	    event         : {
	      text        : "#343A40",
	      border      : "#6C757D",
	      background  : "#E7E7E7"
	    },
	    hookEventColors : () => null, // Added instead of merging setColorEvent of PR#37 since v2.0.0
	  },
	
	  // default view range
	  range           : 3, 
	
	  // numer of timeline rows
	  rows            : 5, 
	
	  // height of row
	  rowHeight       : 40, 
	
	  // width of timeline
	  width           : "auto",
	
	  // height of timeline
	  height          : "auto",
	
	  // min size of <a href="https://www.jqueryscript.net/tags.php?/grid/">grid</a>
	  minGridSize     : 60, 
	
	  // margin size
	  marginHeight    : 2,
	
	  // "left", "center", "right", "current", "latest" or specific event id
	  rangeAlign      : "right",
	
	  // "default", false and selector
	  loader          : "default",
	
	  // loading message
	  loadingMessage  : "",
	
	  // hides scrollbar
	  hideScrollbar   : false,
	
	  // "session" or "local"
	  storage         : "session",
	
	  // loads cached events during reloading
	  reloadCacheKeep : true,
	
	  // zooms the scale of the timeline by double clicking
	  zoom            : false,
	
	  // wraps new scale in the timeline container when zooming
	  wrapScale       : true,
	
	  // 0: Sunday, 1: Monday, ... 6: Saturday
	  firstDayOfWeek  : 0, 
	
	  // "canvas" or "d3.js"
	  engine          : "canvas",
	
	  // avoid validation of the maximum of the scale grids
	  disableLimitter : false,
	
	  // debug mode
	  debug           : false
	  
	});
	  
	  
	 $("#myTimeline").Timeline("show");
	  
	  /***
	   * 6-FIN-TIMELINE
	   * **/
	
		
	});

