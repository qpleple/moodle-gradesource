$(function() {
    var a = [];
    
    $("#name").autocomplete({
    	
    	delay: 0,
    	select: function(event, ui) {
    	  $("#names").append(ui.item.label);
    	  $(this).val("slklk");
    	},
    });
    
    
    function split(val) {
    	return val.split(/,\s*/);
    }
    function extractLast(term) {
    	return split(term).pop();
    }
    
    var availableTags = ["Abbott, Jun Y", "Aguirre, Juan Jose", "Ajani, Nishaad Cheta", "Angelo, Radley Edwi", "Balistreri, Philip P", "Barrientos, Janet", "Barry, Sean F", "Bath, Tyler Everett Turra", "Bhalodia, Niral Vinod", "Bhatia, Kara", "Bochkariov, Bulat", "Breitenstein, Brandon K", "Brew, Connor Michael", "Budiman, Andrew Desmond", "Bui, Tuan D", "Bundalian, Alvin Carino", "Caasi, Kevin Castanar", "Carl, Brandon Lee", "Chatwani, Angelica Bhagwa", "Chen, Edward", "Chen, Ivy", "Chen, Lisa W", "Chen, Mike Kai", "Chen, Yiling", "Chu, David Hahm", "Chung, Addison De", "Chung, Lewis Fu Lei", "Collins, Nicholas Andrew", "Crawford, Eric Richard", "Cross, Crystal Tu", "Dalton, Molly Anne", "Dang, Ken Huu", "Davis, Matthew Alle", "Donley, Andrew Jame", "Duong, Kevin Duy", "Ferbrache, Alexandros Jaso", "Finkel, Scott Andrew", "Fiola, Benjamin Michael", "Flores, Jose Piedad", "Fox, Kevin Coila", "Fung, Richard", "Gao, Song", "Gray, Thomas Stafford", "Hang, Eva", "Hii, Michael Sieng Lung", "Hill, Austin Colema", "Hines, Jackson Anthony", "Hirst, Jordan Eugene", "Ho, Howard Huynh", "Hong, Yoon Pyo", "Hsieh, Eric Yi-Cha", "Huang, Jenny", "Huang, Qi", "Huber, Matthew William", "Jensen, Tyler Jame", "Ke, Albert Jasha", "Kim, April", "Kirby, Michael Craig", "Ko, Tony  Tk", "Kohanfars, Michael Abraham", "Kou, Bryant Jonatha", "Kropff, Kevin Michael", "Kuo, Sharo", "La Fave, Jenner Robert", "Lam, Marcus Haw-Wie", "Lam, Simo", "Larsen, Sarah White", "Lau, Nicholas Matthew", "Lee, Christoph Tenzi", "Lee, Erin M", "Lee, Jessica", "Lei, Benjamin Ki", "Li, Jiajia", "Li, Kewei", "Lisuk, David", "Liu, Joanne Keeng", "Louie, Derek Wai Keith", "Lozhkin, Lev Sergeyevich", "Mack, James Deford", "Maribojoc, Victor Steve", "McGuire, Ashley", "McNamara, Kyle Shigemasa", "Meng, Yinuo", "Murray, Cody Daniel", "Myers-Turnbull, Douglas Joh", "Nath, Siddhartha", "Nevarez, Rafael Jose", "Newman, James Cecil", "Nguyen, Donna", "Nguyen, Dorothy Phuong Khang", "Nguyen, Tai Huu", "Nguyen, Thinh Huu", "Norris, Jacob Robert", "Ochiai, Kazuhito", "Ogut, Irem", "Pak, Keith D", "Park, Yong-Hyu", "Patel, Arjun Angur", "Paveza, Samuel Jame", "Pinkerton, Kristina Ly", "Pinpin, Alejandro Dagoc", "Ponce, Gabriela", "Ransil, Bryan Spelma", "Ren, Xiang", "Rodriguez, Hesler R", "Rodriguez, Iva", "Ruegsegger, Scott Russell", "Sagie, Or", "Selander, Kurt Bradley", "Serrano, Mike", "Shi, David", "Shieh, Steve", "Shiffman, Nadav Zvi", "Shoda, Shigeyuki", "Simone, Matteo Jame", "Sin, Melvin U Fai", "Song, Mingxi", "Soo, Ryan Paul", "Stepanian, Michael", "Su, Jinbo", "Su, Yi", "Sugianto, Yo", "Tang, Congyao", "Tanuwidjaja, Enrico Bern Hardy", "Tao, Feira", "Taylor, Alexander Joseph", "To, Michael", "Tran, Thanh Thao", "Truong, Tony", "Tuckerman, Whitney A", "Valdes, Phoebe H", "Wang, Joe Zhou", "Wilcox, Parry Jennifer", "Wong, Brian Andrew", "Wong, Jonathan Jing-Ning", "Wong, Samson Richard", "Xiao, Zhen Yua", "Xu, Che", "Xu, Daniel", "Yang, Andrew Cal-Wei", "Yao, Stephe", "Young, Benjamin Gee", "Yu, Miao", "Zhang, Xia", "Zhang, Yue", "Zhao, Hui", "Zhou, Xiang", "Zhu, Tanse"]
    
    // don't navigate away from the field on tab when selecting an item
    $("#name-list").bind("keydown", function(event) {
    	if (event.keyCode === $.ui.keyCode.TAB && $(this).data("autocomplete").menu.active) {
    		event.preventDefault();
    	}
    });
    
    $("#name-list").autocomplete({
        minLength: 2,
        delay: 0,
        source: function(request, response) {
        	   // delegate back to autocomplete, but extract the last term
        	   response($.ui.autocomplete.filter(availableTags, extractLast(request.term)));
        },
        focus: function() {
        	   // prevent value inserted on focus
        	   return false;
        },
        select: function(event, ui) {
        	   var terms = split(this.value);
        	   // remove the current input
        	   terms.pop();
        	   // add the selected item
        	   terms.push('"' + ui.item.value + '"');
        	   // add placeholder to get the comma-and-space at the end
        	   terms.push("");
        	   this.value = terms.join(", ");
        	   return false;
        }
    });
}); 