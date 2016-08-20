/*==============================================================================
Global variables
==============================================================================*/
// Final output document
var current_document = { } 

// Used to keep track of who triggered the modal currently visible
modal_source = null

// Used to generate new names for new pages
new_page_counter = 0;

/*==============================================================================
Output related events
==============================================================================*/
/*
    Updates the content of the code preview with the ones of the curren document.
    Has to be called everytime something in the document is changed
*/
function update_output_preview()
{
    var elem = $("#output-preview");
    elem.text(JSON.stringify(current_document, null, '\t'));
    Prism.highlightElement(elem[0]);
}

/*
    Adds a new page to the document
    @param {string} Name of the new page
*/
function add_new_page(page_name, pathname)
{
    current_document["item_pages"].push(
        {
            "id" : page_name,
            "pathname" : pathname,
            "elements" : { }
        });

    update_output_preview();
}

/*
   Updats the page with old_name to new_name
   @param {string} Name of the old page that has to be present
   @param {string} New name for the page
*/
function update_page_name(old_page_name, new_page_name)
{
    for (var i = 0; i < current_document["item_pages"].length; ++i)
    {
        page = current_document["item_pages"][i];
        if (page["id"] == old_page_name)
        {
            page["id"] = new_page_name;
            update_output_preview();
            return;
        }
    }
    console.log("Failed to find page name!")
}

/*
    Removes the page with the specified name
    @param {string} name of the page
*/
function remove_page(page_name)
{
    for (var i = 0; i < current_document["item_pages"].length; ++i)
    {
        page = current_document["item_pages"][i];
        if (page["id"] == page_name)
        {
            current_document["item_pages"].splice(i, 1);
            update_output_preview();
            return;
        }
    }
}

/*
    Adds a new page to the document
    @param {string} Name of the new page
*/
function add_new_display_page(page_name, pathname)
{
    current_document["display_pages"].push(
        {
            "id" : page_name,
            "pathname" : pathname
        });

    update_output_preview();
}

/*
   Updats the page with old_name to new_name
   @param {string} Name of the old page that has to be present
   @param {string} New name for the page
*/
function update_display_page_name(old_page_name, new_page_name)
{
    for (var i = 0; i < current_document["display_pages"].length; ++i)
    {
        page = current_document["display_pages"][i];
        if (page["id"] == old_page_name)
        {
            page["id"] = new_page_name;
            update_output_preview();
            return;
        }
    }
    console.log("Failed to find display page name!")
}

/*
    Removes the page with the specified name
    @param {string} name of the page
*/
function remove_display_page(page_name)
{
    for (var i = 0; i < current_document["display_pages"].length; ++i)
    {
        page = current_document["display_pages"][i];
        if (page["id"] == page_name)
        {
            current_document["display_pages"].splice(i, 1);
            update_output_preview();
            return;
        }
    }
}

function set_display_page_property(page_name, property_key, property_value)
{
    for (var i = 0; i < current_document["display_pages"].length; ++i)
    {
        page = current_document["display_pages"][i];
        if (page["id"] == page_name)
        {
            page[property_key] = property_value;
            update_output_preview();
            return;
        }
    }  
}


/*
    Adds a new page element
    @param {string} name of the element
*/
function add_page_element(page_name, element_name, uri)
{
    for (var i = 0; i < current_document["item_pages"].length; ++i)
    {
        page = current_document["item_pages"][i];
        if (page["id"] == page_name)
        {
            page["elements"][element_name] = uri;
            update_output_preview();
            return;
        }
    }
    console.log("Failed to find page name!")
}

/*
    Removes an existing element from a specific page
    @param {string} name of the element
*/
function remove_page_element(page_name, element_name)
{
    for (var i = 0; i < current_document["item_pages"].length; ++i)
    {
        page = current_document["item_pages"][i];
        if (page["id"] == page_name)
        {
            delete page["elements"][element_name];
            update_output_preview();
            return;
        }
    }
}

/*==============================================================================
DOM-related events ( Some of them have to be reloaded as page is dynamic)
==============================================================================*/
// Binds all event to pages. Needs to be called everytime new pages / items
// are added to make event works
function bind_page_events()
{
    $(".remove-page").click(function() {
        var page_root = $(this).closest(".new-page-root");
        page_name_elem = page_root.find(".page-name");
        remove_page(page_name_elem.text());
        page_root.remove();
    });
    
    $(".remove-display-page").click(function() {
        var page_root = $(this).closest(".new-page-root");
        page_name_elem = page_root.find(".page-name");
        remove_display_page(page_name_elem.text());
        page_root.remove();
    });

    $(".page-name-input").bind("change paste keyup", function()
    {
        var elem = $(this);
        var page_name_elem = elem.parent().parent().parent().prev().children(".page-name");
        update_page_name(page_name_elem.text(), elem.val());
        page_name_elem.text(elem.val());
    });
    
    $(".display-page-name-input").bind("change paste keyup", function()
    {
        var elem = $(this);
        var page_name_elem = elem.parent().parent().parent().prev().children(".page-name");
        update_display_page_name(page_name_elem.text(), elem.val());
        page_name_elem.text(elem.val());
    });
    
    $(".page-link-input").bind("change paste keyup", function()
    {
        var elem = $(this);
        var page_name_elem = elem.parent().parent().parent().prev().children(".page-name");
        set_display_page_property(page_name_elem.text(), "item_id", elem.val());
    });
    
    $(".page-action-input").bind("change paste keyup", function()
    {
        var elem = $(this);
        var page_name_elem = elem.parent().parent().parent().prev().children(".page-name");
        set_display_page_property(page_name_elem.text(), "action", elem.val());
    });
    
    $(".page-args-input").bind("change paste keyup", function()
    {
        var elem = $(this);
        var page_name_elem = elem.parent().parent().parent().prev().children(".page-name");
        set_display_page_property(page_name_elem.text(), "args", elem.val());
    });
    
    $(".page-method-input").bind("change paste keyup", function()
    {
        var elem = $(this);
        var page_name_elem = elem.parent().parent().parent().prev().children(".page-name");
        set_display_page_property(page_name_elem.text(), "method", elem.val());
    });
    
    $(".item-uri").click(function()
    {
        var str_to_eval = "(" + generate_uri_from_element.toString() + ")($0)";
        var src_elem = $(this);
        chrome.devtools.inspectedWindow.eval(str_to_eval, { }, function(result) 
        {
            var page_name_elem = src_elem.parent().parent().parent().prev().children(".page-name");
            set_display_page_property(page_name_elem.text(), "item_uri", JSON.parse(result)["uri"]);
            src_elem.removeClass("red");
            src_elem.addClass("green");
        });
    });
    
    $(".next-uri").click(function()
    {
        var str_to_eval = "(" + generate_uri_from_element.toString() + ")($0)";
        var src_elem = $(this);
        chrome.devtools.inspectedWindow.eval(str_to_eval, { }, function(result) 
        {
            var page_name_elem = src_elem.parent().parent().parent().prev().children(".page-name");
            set_display_page_property(page_name_elem.text(), "next_uri", JSON.parse(result)["uri"]);
            src_elem.removeClass("red");
            src_elem.addClass("green");
        }); 
    });

    $(".item-page-remove").click(function() {
        page_name_elem = $(this).closest(".new-page-root").find(".page-name");
        item_name_elem = $(this).parent().children(".item-name");
        remove_page_element(page_name_elem.text(), item_name_elem.text());
        $(this).closest(".collection-item").remove();
    });

    $(".modal-trigger").click(function()
    {
        // Saving source
        modal_source = $(this);
    });

    // Enabling modals
    $(document).ready(function() {
      $('.modal-trigger').leanModal();
    });
}

// Outside modifiable DOM
$("#new-page-item").click(function() {
    if (modal_source != null)
    {
        var source = $("#new-page-item-tpl").html();
        var tpl = Handlebars.compile(source);
        var new_item_html = tpl({ "name" : $("#item-add-page-name").val() });
        modal_source.parent().parent().parent().append(new_item_html);
        bind_page_events();

        // Retrieveing name
        page_name_elem = modal_source.closest(".new-page-root").find(".page-name");
        add_page_element(page_name_elem.text(), $("#item-add-page-name").val(), $("#new-element-uri").text());
        toastr["success"]("Successfully added new element:\n" + $("#item-add-page-name").val());
        
        $("#item-add-page-name").val("");
        $("#new-element-uri").text("uri");
        $("#take-snapshot").removeClass("green");
        $("#take-snapshot").addClass("red");
    }
    else
    {
        console.log("modal_source was null this is unexpected behavior");
    }
});

$("#add-page").click(function() {
    new_name = "New page" + (new_page_counter++).toString();
    var source = $("#new-page-tpl").html();
    var tpl = Handlebars.compile(source);
    var new_page_html = tpl({ "name" : new_name });
    $("#pages").children("ul").append(new_page_html);

    var str_to_eval = "(" + get_url_pathname.toString() + ")()";
    chrome.devtools.inspectedWindow.eval(str_to_eval, { }, function(result) 
    { 
        add_new_page(new_name, JSON.parse(result)["url"]);
        bind_page_events();
    });

});

$("#add-display-page").click(function() {
    new_name = "New display page" + (new_page_counter++).toString();
    var source = $("#new-display-page-tpl").html();
    var tpl = Handlebars.compile(source);
    var new_page_html = tpl({ "name" : new_name });
    $("#pages").children("ul").append(new_page_html);
    
    var str_to_eval = "(" + get_url_pathname.toString() + ")()";
    chrome.devtools.inspectedWindow.eval(str_to_eval, { }, function(result) 
    { 
        add_new_display_page(new_name, JSON.parse(result)["url"]);
        bind_page_events();
    });
});


$("#take-snapshot").click(function() {
    var str_to_eval = "(" + generate_uri_from_element.toString() + ")($0)";
    chrome.devtools.inspectedWindow.eval(str_to_eval, { }, function(result) 
    { 
        $("#new-element-uri").text(JSON.parse(result)["uri"]);
        $("#take-snapshot").removeClass("red");
        $("#take-snapshot").addClass("green");
    });
});

$("#download-btn").click(function()
{
    output_elem = $("#output-name");
    if (!output_elem.val() || 0 == output_elem.val())
    {
        $("#output-name-label").addClass("active"); // Avoid overlapping content
        output_elem.val("output.json");
    }

    // Checking if the string ends with .json
    if (!output_elem.val().endsWith(".host.config"))
    {
        output_elem.val(output_elem.val() + ".host.config");
    }
    
    var blob = new Blob([JSON.stringify(current_document, null, '\t')], { type : "text/plain;charset=utf-8"});
    saveAs(blob, output_elem.val());
});

function create_sliders()
{
    dtt_el = document.getElementById("rating-depth-trust-threshold");
    noUiSlider.create(dtt_el, 
    {
        start : 15,
        step : 1,
        range: { 'min' : [0], 'max' : [40] }
    });
    
    dtt_el.noUiSlider.on('update', function(values, handle)
    {
        current_document["rating"]["depth_trust_threshold"] = values[0]; 
        update_output_preview();
        $("#rating-depth-trust-threshold-val").text(values[0]);
    });
    
    
    itr_el = document.getElementById("rating-id-trust-ratio");
    noUiSlider.create(itr_el, 
    {
        start : 15,
        step : 0.01,
        range: { 'min' : [0], 'max' : [1] }
    });
    
    itr_el.noUiSlider.on('update', function(values, handle)
    {
        current_document["rating"]["id_trust_ratio"] = values[0]; 
        update_output_preview();
        $("#rating-id-trust-ratio-val").text(values[0]);
    });
    
    
    ctr_el = document.getElementById("rating-class-trust-ratio");
    noUiSlider.create(ctr_el, 
    {
        start : 15,
        step : 0.01,
        range: { 'min' : [0], 'max' : [1] }
    });
    
    ctr_el.noUiSlider.on('update', function(values, handle)
    {
        current_document["rating"]["class_trust_ratio"] = values[0]; 
        update_output_preview();
        $("#rating-class-trust-ratio-val").text(values[0]);
    });
    
    
    mt_el = document.getElementById("rating-mitigation-threshold");
    noUiSlider.create(mt_el, 
    {
        start : 2,
        step : 1,
        range: { 'min' : [0], 'max' : [4] }
    });
    
    mt_el.noUiSlider.on('update', function(values, handle)
    {
        current_document["rating"]["mitigation-threshold"] = values[0]; 
        update_output_preview();
        $("#rating-mitigation-threshold-val").text(values[0]);
    });
    
    
    tt_el = document.getElementById("rating-trust-threshold");
    noUiSlider.create(tt_el,
    {
        start : 0.4,
        step : 0.01,
        range: { 'min' : [0], 'max' : [1] }
    });
    
    tt_el.noUiSlider.on('update', function(values, handle)
    {
        current_document["rating"]["trust_treshold"] = values[0]; 
        update_output_preview();
        $("#rating-trust-threshold-val").text(values[0]);
    });
    
    
    fma_el = document.getElementById("rating-full-match-advantage");
    noUiSlider.create(fma_el, 
    {
        start : 0.5,
        step : 0.01,
        range: { 'min' : [0], 'max' : [2] }
    });
    
    fma_el.noUiSlider.on('update', function(values, handle)
    {
        current_document["rating"]["full_match_advantage"] = values[0]; 
        update_output_preview();
        $("#rating-full-match-advantage-val").text(values[0]);
    });
}

// Some initialization
bind_page_events();
update_output_preview();

// Setting base url for page
chrome.devtools.inspectedWindow.eval("(" + get_url_hostname.toString() + ")($0)", { }, function(result)
{
     current_document["base_url"] = JSON.parse(result)["url"];
     update_output_preview();
});

current_document["item_pages"] = [];
current_document["display_pages"] = [];
current_document["rating"] = {};

create_sliders();
