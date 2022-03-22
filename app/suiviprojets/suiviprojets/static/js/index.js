

$(function(){
	
	
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
	
	var popup=popupAdmin("voile","window");
	
	$("#close-window").on('click', function (event) {
		popup.hide();
	});
	/****
	*
	*   1. AJAX gestion de la pagination
	*
	*****/
	var __fillfield= function(elt,value,data_id,opts){
				try{
					/*var elt=element.children().first();
					elt.attr({"data-id":data_id,
							"id":"td-lien-"+id});*/
					$(elt).attr({"data_id":data_id});
					switch($(elt).get(0).nodeName){
						case 'SELECT':
							$(elt).empty();
							for(var option in opts){
								var default_val=(value == 'empty')? 5 : parseInt(value);
								var selected=(default_val == parseInt(opts[option].id))?"selected":"";
								$(elt).append("<option value='"+opts[option].id+"'"+selected+">"+
																opts[option].indice+
												"</option>");
							}
							break;
						default:
							if(value=="" || value=='empty'){
								$(elt).empty();
							 }else{
								$(elt).empty().html(value);
							}
							try{
								$(elt).find(".edit").on("click",function(event){
																		showdetail(this,event);
																	});

							}catch(e){
								return false;
							}
							break;
					}
				}
				catch(error){
						console.log(error);
				}
			};
	var __filldatas=function(cible,objet,result,options){

		  var lines=$(cible);
		  var nbeltsppage=parseInt($("#nb-elts-pages").val());
		  var nb_lignes_vides=nbeltsppage-result.length;

		  $.each(result,function(index,data){
			  
			  $(lines[index]).attr({"id":"line-"+data['id'],"data-id":data["id"]});
			  if($(lines[index]).find(".details>a").length==0){
				   $(lines[index]).find(".details").empty().html("<a href='/details/"+data["id"]+"/'>Voir</a>"); 
			  //}else if($(lines[index]).find(".client>a").length==0){
				  
					$(lines[index]).find(".client").attr({"data_id":data["id"]});
					$(lines[index]).find(".client").empty().html("<a href='/client/"+data['client']['id']+"/'>"+data['client']['nom']+"</a>");
			  }else{
				  console.log("3");
				  $(lines[index]).find(".details>a").attr({"href":"/details/"+data["id"]+"/"});
				  $(lines[index]).find(".client>a").attr({"href":"/client/"+data['client']['id']+"/"})
				  $(lines[index]).find(".client>a").empty().html(data['client']['nom']);
		      }
		      delete data.client
			  for(field in data){
				__fillfield($(lines[index]).find("."+field),data[field],data['id'],field+"-"+data['id'],options);
			 }
			 
		  });
		  /*! Dans le cas ou le nb de lignes vides est > 0, denniere page il remplit
		   * les lignes de cases vides */
		  /*console.log(nb_lignes_vides);*/
		  if(nb_lignes_vides>0){
				for(var index=(nbeltsppage-(nb_lignes_vides));index<nbeltsppage;index++){
					$(lines[index]).attr({"id":"line-empty-"+index,"data-id":"empty"});
					$.each($(lines[index]).find(".cell"),function(ind,elt){
							 __fillfield($(elt),"empty",index,"empty-"+index,options)
					});
				}
		}
	};
	var click=function(target){
         var link=$(target).find('a');
         var num_page=$(link).attr('data-page');
         var csrf_token=$("input[name=csrfmiddlewaretoken]").val();
         var objet=$(target).find("#objet").val();
         console.log(objet);
         $.post('/'+objet+'s/page/',
               {'csrfmiddlewaretoken':csrf_token,
                'num_page':num_page})
               .done(function(resp){
                 var json=JSON.parse(resp);
                 /*!console.log(json);*/
                  /*! fill the different fields */
                  __filldatas(".line",objet,json.liste,json.indices);
                  /*! fill pagination area */
                  $('.paginator').empty().html(json.pagination);
                  $('#nb-elts').empty().html(json.total_elts);
                  $('.page-item').on('click',function(event){event.preventDefault();event.stopPropagation();click(this);});
                })
              .fail(function(error){
                    console.log(error);
                });

            }; 
     /*!***
      *   Attachement aux elements de liens de pages
      * ****/
    $(".page-item").on('click',function(event){event.preventDefault();event.stopPropagation();click(this)});
    /*!****
     *    Fin 1 AJAX gestion des pages
     * ****/
     
    /****
	*
	*   2. AJAX gestion de la liste
	*
	*****/
	$("#search").on("click",function(event){
		event.preventDefault();
		var objet=$("#objet").val();
		var datas={'csrfmiddlewaretoken':$("input[name='csrfmiddlewaretoken']").val(),
					'num_armoire':$("#num_armoire").val(),
					'nom':$("#nom").val(),
					'forfait':$("#forfait").val()
				};
		$.post('/search/',datas,function(response){
			 var json=JSON.parse(response);
			/*__filldatas(".line",json.liste,json.indices);*/
			  /*! fill pagination area */
			__filldatas(".line",objet,json.liste,json.indices);
			$('#nb-elts').html(json.total_elts);
			$('.paginator').html(json.pagination);
			$(".page-item").on('click',function(event){event.preventDefault();event.stopPropagation();click(this);});

		});
		
	});
	
    $(".sort").on('click',function(event){
        event.preventDefault();
        event.stopPropagation();
        var elt=this;
        var sens=$(elt).attr("data-sens");
        var csrf_token=$("input[name=csrfmiddlewaretoken]").val();
        var objet=$("#objet").val();
        params={'csrfmiddlewaretoken':csrf_token,
                'field':$(this).attr('data-field'),
                'sens':sens,
                };
       $.post("/projects/sort/",params,function(response){
                        var json=JSON.parse(response);
                        __filldatas(".line",objet,json.liste,json.indices);
                         $('.paginator').html(json.pagination);
                         $(".lien-page").on('click',function(event){event.preventDefault();click(this,event);});
                         /* on reinitialise les valeurs de sens des fleches */
                         $(".sort[data-sens='desc']").removeClass("desc");
                         $(".sort[data-sens='desc']").addClass("asc");
                         /* on change la valeur du sens dans le data-sens */
                         $(elt).attr({"data-sens":(sens == "asc")?"desc":"asc"});
                         $(elt).addClass((sens == "asc")?"desc":"asc");
                         $(elt).removeClass(sens);


        });


    });
    
    var change=function(target){
			        var nb=$(target).val();
			        var params={'csrfmiddlewaretoken':csrf_token,
			                    'nb':nb};
			        $.post('/projects/nb/',params,function(response){
			                    $("#liste-items").empty().html(response);
			                    $(".page-item").on('click',function(event){event.preventDefault();click(this);});
			                    $("#nb-elts-pages").val(nb);
			                    $("#nb-elts-pages").on('change',function(event){event.preventDefault();change(this);});
			        });


    };
    $("#nb-elts-pages").on("change",function(event){
						console.log("marche");
                        event.preventDefault();
                        event.stopPropagation();
                        change(this);
    });
    
     /****
     * 2-Fin-Liste
     ************/
     
     /****
	 * 3-Traitement des formulaires 
	 * **/
	 $("#add-contact,#add-echange,#add-prestation,#add-tache").on("click",function(event){
		event.preventDefault();
		event.stopPropagation();
		var datas={
			csrfmiddlewaretoken:$("input[name=csrfmiddlewaretoken]").val(),
			objet      :$(event.target).attr("data-objet"),
			type_projet:$(event.target).attr("data-type_projet"),
			projet     :$(event.target).attr("data-projet"),
			client     :$(event.target).attr("data-client")
		};
		$.post("/add/",datas).done(function(response){
			popup.show(response);
			
		});
		 
	 });
	 $("#submit").on("click",function(event){
		event.preventDefault();
		event.stopPropagation();
		 
		})  
     /*****
      * 4-Calendrier
      * ***/
      
      try{
		var calendar = new FullCalendar.Calendar(document.getElementById("calendar"),{height:500,
																				contentHeight:110,
																				aspectRatio:0.5,
																				expandRows:true,
																				eventSources:[eventscp,eventsct,eventsce],
																				initialView:'dayGridMonth',
																				eventContent:function(arg){
																						let statut_marker=document.createElement("span");
																						statut_marker.setAttribute("class","statut");
																						statut_marker.setAttribute("style","background-color:#"+arg.event.extendedProps.statut+";");
																						let content=document.createElement("p");
																						content.setAttribute("title",arg.event.extendedProps.description);
																						content.innerHTML=arg.event.title;
																						let arrayofDomNodes=[statut_marker,content];
																						return {domNodes:arrayofDomNodes};
																					
																				}
																				});
		calendar.render();
	}
	catch(error){
			console.log("");
	}
	
    /****
     * 4-Fin-Calendrier
     * **/
	
	
});
