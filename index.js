$(document).ready(function()
{
   console.log("Document ready");

   $.ajaxSetup({ cache: false });

   var findSubmit = $("#formfindersubmit");
   findSubmit.click(function()
   {
      var species = $("#formfinderinput").val().toLowerCase();
      var url = encodeURI("https://pokeapi.co/api/v2/pokemon-species/" + species);
      $.getJSON(url, function(data)
      {
         var forms = "Forms: \n";
         for(var i = 0; i < data.varieties.length; i++)
            forms += "\n" + data.varieties[i].pokemon.name;
         alert(forms);
      }).fail(function() { alert("Couldn't find pokemon"); });
   });

   $.getJSON("data.json", function(data)
   {
      var header = $("h1");
      header.text(data.user + "'s " + header.text());

      var pkmTable = $("#pokemon");
      SetupPokeTable(pkmTable, data);
   });
});

function SetupPokeTable(pkmTable, data)
{
   pkmTable.DataTable ({
      "data" : data.list,
      "pageLength" : 50,
      "order" : [[ 2, "asc" ]],
      "autoWidth" : true,
      "columns" : [
         { "data" : "thumb",
            "orderable" : false,
            "class" : "preview",
            "render" : function(data, type, row, meta)
            {
               var link = $("<a></a>");
               var image = $("<img>");
               link.attr("href", encodeURI(row.path));
               image.attr("src", encodeURI(data));
               link.append(image);
               return link[0].outerHTML;
            }
         },
         { "data" : "name",
            "class" : "name",
            "render" : function(data, type, row, meta)
            {
               var link = $("<a></a>");
               link.text(data);
               link.attr("target", "blank");
               link.attr("href", encodeURI(
               "https://www.serebii.net/pokemon/" + row["species"] + "/"));
               return link[0].outerHTML;
            }
         },
         { "data" : "number",
            "class" : "number"
         },
         { "data" : "generation",
            "class" : "generation"
         },
         { "data" : "created",
            "class" : "created",
            "render" : function(data)
            {
               return data.slice(0, 10);
            }
         },
      ]
   });
}
