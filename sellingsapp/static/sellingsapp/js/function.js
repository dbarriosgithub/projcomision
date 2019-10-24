$(document).ready(function () {
    var param_field = '';

    // ------------------------------------------------
    //   Evento que se activa con el botón de búsqueda
    // ------------------------------------------------
    $("#basic-addon1").click(function () {
        $("#frmsearch").submit();
    });

    // ---------------------------------------------------
    //   Función que permite autocompletar una búsqueda
    // ---------------------------------------------------    
    $('#search_text').keyup(function () {
        param_field = $('#search_field').val();
        $(this).autocomplete({
            source: "http://" + location.host + "/campaign/auto_complete_search/?field=" + param_field,
            select: function (event, ui) {
                $("#search_text").val(ui.item.value);
                $("#frmsearch").submit();
            }
        });
    });

    $("#id_product_name").change(function () {
         cant = 0;

        if ($(this).val() == 'oneplay')
            cant = 1;
        else if ($(this).val() == 'duoplay')
            cant = 2;
        else if ($(this).val() == 'tripleplay')
            cant = 3;

        $("#id_product_cant").val(cant);
    });
});