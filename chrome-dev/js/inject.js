function generate_uri_from_element(element)
{
    var uri = '';
    node = element;
    while (node) 
    {
        uri += '<' + node.tagName.toLowerCase() + '>';
        uri += node.id;
        uri += ','
        uri += node.className;

        node = node.parentElement;
    }
    
    return JSON.stringify({ 'uri' : uri});
}