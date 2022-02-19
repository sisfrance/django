$(function () {
	
	/*****
 * CREE LA FENETRE DETAILS Ingredients et Etapes
 * ***/


 function popupAdmin(voile, id) {
	  return {
	    show: function show(htmldatas) {
	      $("#" + voile).addClass("obscur");
	      $("#" + id).css({
	        'width': '800px',
	        'minHeight': window.innerHeight - 100 + 'px'
	      });
	      $("#" + id + "-content").html(htmldatas);
	      /*tinyMCE.execCommand('mceAddEditor', false, 'etape_description');*/
	    },
	    hide: function hide() {
	      $("#" + id + "-content").empty();
	      $("#" + id).css({
	        'width': '0',
	        'height': '0'
	      });
	      /*tinyMCE.execCommand('mceRemoveEditor', false, 'etape_description');*/
	      setTimeout(function () {
	        $("#" + voile).removeClass("obscur");
	      }, 600);
	    }
	  };
	};
	
});
