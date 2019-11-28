$(document).ready(function()
{
   console.log("Document ready");

   $.ajaxSetup({ cache: false });

   $.getJSON("data.json", function(data)
   {
      var header = $("h1");
      header.text(data.user + "'s " + header.text());

      var pkmTable = $("#pokemon");

      pkmTable.DataTable ({
         "data" : data.list,
         "pageLength" : 50,
         "order" : [[ 2, "asc" ]],
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
              "class" : "name" 
            },
            { "data" : "number",
              "class" : "number"
            },
         ]
      });
   });
});
