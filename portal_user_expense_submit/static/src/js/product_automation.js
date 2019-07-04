odoo.define('portal_user_expense_submit.product_automation', function (require) {
"use strict";
 
require('web.dom_ready');
$("select[name='product_id']").on("change", function (){
         var product=$(this).val();
         var unitprice = $(this).children("option:selected").attr('data-unit-price')
         $("#unit_amount").val(unitprice);



         var unitmeasure = $(this).children("option:selected").attr('data-unit-measure')
         $("select[name='product_uom_id']").find("option[value="+unitmeasure+"]").attr("selected","selected")
       });


});