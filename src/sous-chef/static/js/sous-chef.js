/**
 * jQuery Formset 1.3-pre
 * @author Stanislaus Madueke (stan DOT madueke AT gmail DOT com)
 * @requires jQuery 1.2.6 or later
 *
 * Copyright (c) 2009, Stanislaus Madueke
 * All rights reserved.
 *
 * Licensed under the New BSD License
 * See: http://www.opensource.org/licenses/bsd-license.php
 */
;(function($) {
    $.fn.formset = function(opts)
    {
        var options = $.extend({}, $.fn.formset.defaults, opts),
            flatExtraClasses = options.extraClasses.join(' '),
            totalForms = $('#id_' + options.prefix + '-TOTAL_FORMS'),
            maxForms = $('#id_' + options.prefix + '-MAX_NUM_FORMS'),
            minForms = $('#id_' + options.prefix + '-MIN_NUM_FORMS'),
            childElementSelector = 'input,select,textarea,label,div',
            $$ = $(this),

            applyExtraClasses = function(row, ndx) {
                if (options.extraClasses) {
                    row.removeClass(flatExtraClasses);
                    row.addClass(options.extraClasses[ndx % options.extraClasses.length]);
                }
            },

            updateElementIndex = function(elem, prefix, ndx) {
                var idRegex = new RegExp(prefix + '-(\\d+|__prefix__)-'),
                    replacement = prefix + '-' + ndx + '-';
                if (elem.attr("for")) elem.attr("for", elem.attr("for").replace(idRegex, replacement));
                if (elem.attr('id')) elem.attr('id', elem.attr('id').replace(idRegex, replacement));
                if (elem.attr('name')) elem.attr('name', elem.attr('name').replace(idRegex, replacement));
            },

            hasChildElements = function(row) {
                return row.find(childElementSelector).length > 0;
            },

            showAddButton = function() {
                return maxForms.length == 0 ||   // For Django versions pre 1.2
                    (maxForms.val() == '' || (maxForms.val() - totalForms.val() > 0));
            },

            /**
            * Indicates whether delete link(s) can be displayed - when total forms > min forms
            */
            showDeleteLinks = function() {
                return minForms.length == 0 ||   // For Django versions pre 1.7
                    (minForms.val() == '' || (totalForms.val() - minForms.val() > 0));
            },

            insertDeleteLink = function(row) {
                var delCssSelector = $.trim(options.deleteCssClass).replace(/\s+/g, '.'),
                    addCssSelector = $.trim(options.addCssClass).replace(/\s+/g, '.');
                if (row.is('TR')) {
                    // If the forms are laid out in table rows, insert
                    // the remove button into the last table cell:
                    row.children(':last').append('<a class="' + options.deleteCssClass +'" href="javascript:void(0)">' + options.deleteText + '</a>');
                } else if (row.is('UL') || row.is('OL')) {
                    // If they're laid out as an ordered/unordered list,
                    // insert an <li> after the last list item:
                    row.append('<li><a class="' + options.deleteCssClass + '" href="javascript:void(0)">' + options.deleteText +'</a></li>');
                } else {
                    // Otherwise, just insert the remove button as the
                    // last child element of the form's container:
                    row.append('<a class="' + options.deleteCssClass + '" href="javascript:void(0)">' + options.deleteText +'</a>');
                }
                // Check if we're under the minimum number of forms - not to display delete link at rendering
                if (!showDeleteLinks()){
                    row.find('a.' + delCssSelector).hide();
                }

                row.find('a.' + delCssSelector).click(function() {
                    var row = $(this).parents('.' + options.formCssClass),
                        del = row.find('input:hidden[id $= "-DELETE"]'),
                        buttonRow = row.siblings("a." + addCssSelector + ', .' + options.formCssClass + '-add'),
                        forms;
                    if (del.length) {
                        // We're dealing with an inline formset.
                        // Rather than remove this form from the DOM, we'll mark it as deleted
                        // and hide it, then let Django handle the deleting:
                        del.val('on');
                        row.hide();
                        forms = $('.' + options.formCssClass).not(':hidden');
                    } else {
                        row.remove();
                        // Update the TOTAL_FORMS count:
                        forms = $('.' + options.formCssClass).not('.formset-custom-template');
                        totalForms.val(forms.length);
                    }
                    for (var i=0, formCount=forms.length; i<formCount; i++) {
                        // Apply `extraClasses` to form rows so they're nicely alternating:
                        applyExtraClasses(forms.eq(i), i);
                        if (!del.length) {
                            // Also update names and IDs for all child controls (if this isn't
                            // a delete-able inline formset) so they remain in sequence:
                            forms.eq(i).find(childElementSelector).each(function() {
                                updateElementIndex($(this), options.prefix, i);
                            });
                        }
                    }
                    // Check if we've reached the minimum number of forms - hide all delete link(s)
                    if (!showDeleteLinks()){
                        $('a.' + delCssSelector).each(function(){$(this).hide();});
                    }
                    // Check if we need to show the add button:
                    if (buttonRow.is(':hidden') && showAddButton()) buttonRow.show();
                    // If a post-delete callback was provided, call it with the deleted form:
                    if (options.removed) options.removed(row);
                    return false;
                });
            };

        $$.each(function(i) {
            var row = $(this),
                del = row.find('input:checkbox[id $= "-DELETE"]');
            if (del.length) {
                // If you specify "can_delete = True" when creating an inline formset,
                // Django adds a checkbox to each form in the formset.
                // Replace the default checkbox with a hidden field:
                if (del.is(':checked')) {
                    // If an inline formset containing deleted forms fails validation, make sure
                    // we keep the forms hidden (thanks for the bug report and suggested fix Mike)
                    del.before('<input type="hidden" name="' + del.attr('name') +'" id="' + del.attr('id') +'" value="on" />');
                    row.hide();
                } else {
                    del.before('<input type="hidden" name="' + del.attr('name') +'" id="' + del.attr('id') +'" />');
                }
                // Hide any labels associated with the DELETE checkbox:
                $('label[for="' + del.attr('id') + '"]').hide();
                del.remove();
            }
            if (hasChildElements(row)) {
                row.addClass(options.formCssClass);
                if (row.is(':visible')) {
                    insertDeleteLink(row);
                    applyExtraClasses(row, i);
                }
            }
        });

        if ($$.length) {
            var hideAddButton = !showAddButton(),
                addButton, template;
            if (options.formTemplate) {
                // If a form template was specified, we'll clone it to generate new form instances:
                template = (options.formTemplate instanceof $) ? options.formTemplate : $(options.formTemplate);
                template.removeAttr('id').addClass(options.formCssClass + ' formset-custom-template');
                template.find(childElementSelector).each(function() {
                    updateElementIndex($(this), options.prefix, '__prefix__');
                });
                insertDeleteLink(template);
            } else {
                // Otherwise, use the last form in the formset; this works much better if you've got
                // extra (>= 1) forms (thnaks to justhamade for pointing this out):
                template = $('.' + options.formCssClass + ':last').clone(true).removeAttr('id');
                template.find('input:hidden[id $= "-DELETE"]').remove();
                // Clear all cloned fields, except those the user wants to keep (thanks to brunogola for the suggestion):
                template.find(childElementSelector).not(options.keepFieldValues).each(function() {
                    var elem = $(this);
                    // If this is a checkbox or radiobutton, uncheck it.
                    // This fixes Issue 1, reported by Wilson.Andrew.J:
                    if (elem.is('input:checkbox') || elem.is('input:radio')) {
                        elem.attr('checked', false);
                    } else {
                        elem.val('');
                    }
                });
            }
            // FIXME: Perhaps using $.data would be a better idea?
            options.formTemplate = template;

            if ($$.is('TR')) {
                // If forms are laid out as table rows, insert the
                // "add" button in a new table row:
                var numCols = $$.eq(0).children().length,   // This is a bit of an assumption :|
                    buttonRow = $('<tr><td colspan="' + numCols + '"><a class="' + options.addCssClass + '" href="javascript:void(0)">' + options.addText + '</a></tr>')
                                .addClass(options.formCssClass + '-add');
                $$.parent().append(buttonRow);
                if (hideAddButton) buttonRow.hide();
                addButton = buttonRow.find('a');
            } else {
                // Otherwise, insert it immediately after the last form:
                $$.filter(':last').after('<a class="' + options.addCssClass + '" href="javascript:void(0)">' + options.addText + '</a>');
                addButton = $$.filter(':last').next();
                if (hideAddButton) addButton.hide();
            }
            addButton.click(function() {
                var formCount = parseInt(totalForms.val()),
                    row = options.formTemplate.clone(true).removeClass('formset-custom-template'),
                    buttonRow = $($(this).parents('tr.' + options.formCssClass + '-add').get(0) || this)
                    delCssSelector = $.trim(options.deleteCssClass).replace(/\s+/g, '.');
                applyExtraClasses(row, formCount);
                row.insertBefore(buttonRow).show();
                row.find(childElementSelector).each(function() {
                    updateElementIndex($(this), options.prefix, formCount);
                });
                totalForms.val(formCount + 1);
                // Check if we're above the minimum allowed number of forms -> show all delete link(s)
                if (showDeleteLinks()){
                    $('a.' + delCssSelector).each(function(){$(this).show();});
                }
                // Check if we've exceeded the maximum allowed number of forms:
                if (!showAddButton()) buttonRow.hide();
                // If a post-add callback was supplied, call it with the added form:
                if (options.added) options.added(row);
                return false;
            });
        }

        return $$;
    };

    /* Setup plugin defaults */
    $.fn.formset.defaults = {
        prefix: 'form',                  // The form prefix for your django formset
        formTemplate: null,              // The jQuery selection cloned to generate new form instances
        addText: 'add another',          // Text for the add link
        deleteText: 'remove',            // Text for the delete link
        addCssClass: 'add-row',          // CSS class applied to the add link
        deleteCssClass: 'delete-row',    // CSS class applied to the delete link
        formCssClass: 'dynamic-form',    // CSS class applied to each form in a formset
        extraClasses: [],                // Additional CSS classes, which will be applied to each form in turn
        keepFieldValues: '',             // jQuery selector for fields whose values should be kept when the form is cloned
        added: null,                     // Function called each time a new form is added
        removed: null                    // Function called each time a form is deleted
    };
})(jQuery);

/*
	A simple, lightweight jQuery plugin for creating sortable tables.
	https://github.com/kylefox/jquery-tablesort
	Version 0.0.7
*/
!function(t){t.tablesort=function(e,s){var i=this;this.$table=e,this.$thead=this.$table.find("thead"),this.settings=t.extend({},t.tablesort.defaults,s),this.$sortCells=this.$thead.length>0?this.$thead.find("th:not(.no-sort)"):this.$table.find("th:not(.no-sort)"),this.$sortCells.bind("click.tablesort",function(){i.sort(t(this))}),this.index=null,this.$th=null,this.direction=null},t.tablesort.prototype={sort:function(e,s){var i=new Date,n=this,o=this.$table,l=this.$thead.length>0?o.find("tbody tr"):o.find("tr").has("td"),a=o.find("tr td:nth-of-type("+(e.index()+1)+")"),r=e.data().sortBy,d=[],h=a.map(function(s,i){return r?"function"==typeof r?r(t(e),t(i),n):r:null!=t(this).data().sortValue?t(this).data().sortValue:t(this).text()});0!==h.length&&("asc"!==s&&"desc"!==s?this.direction="asc"===this.direction?"desc":"asc":this.direction=s,s="asc"==this.direction?1:-1,n.$table.trigger("tablesort:start",[n]),n.log("Sorting by "+this.index+" "+this.direction),n.$table.css("display"),setTimeout(function(){n.$sortCells.removeClass(n.settings.asc+" "+n.settings.desc);for(var r=0,c=h.length;c>r;r++)d.push({index:r,cell:a[r],row:l[r],value:h[r]});d.sort(function(t,e){return t.value>e.value?1*s:t.value<e.value?-1*s:0}),t.each(d,function(t,e){o.append(e.row)}),e.addClass(n.settings[n.direction]),n.log("Sort finished in "+((new Date).getTime()-i.getTime())+"ms"),n.$table.trigger("tablesort:complete",[n]),n.$table.css("display")},h.length>2e3?200:10))},log:function(e){(t.tablesort.DEBUG||this.settings.debug)&&console&&console.log&&console.log("[tablesort] "+e)},destroy:function(){return this.$sortCells.unbind("click.tablesort"),this.$table.data("tablesort",null),null}},t.tablesort.DEBUG=!1,t.tablesort.defaults={debug:t.tablesort.DEBUG,asc:"sorted ascending",desc:"sorted descending"},t.fn.tablesort=function(e){var s,i;return this.each(function(){s=t(this),i=s.data("tablesort"),i&&i.destroy(),s.data("tablesort",new t.tablesort(s,e))})}}(window.Zepto||window.jQuery);
!function(e,t,a,n){e.fn.calendar=function(t){var r,o=e(this),i=o.selector||"",l=(new Date).getTime(),u=[],s=arguments[0],d="string"==typeof s,p=[].slice.call(arguments,1);return o.each(function(){var o,c,f=e.isPlainObject(t)?e.extend(!0,{},e.fn.calendar.settings,t):e.extend({},e.fn.calendar.settings),m=f.className,g=f.namespace,h=f.selector,y=f.formatter,v=f.parser,D=f.metadata,b=f.error,C="."+g,M="module-"+g,w=e(this),x=w.find(h.input),k=w.find(h.popup),T=w.find(h.activator),H=this,I=w.data(M),N=!1,F=!1;c={initialize:function(){c.debug("Initializing calendar for",H),o=c.get.isTouch(),c.setup.popup(),c.setup.inline(),c.setup.input(),c.setup.date(),c.create.calendar(),c.bind.events(),c.instantiate()},instantiate:function(){c.verbose("Storing instance of calendar"),I=c,w.data(M,I)},destroy:function(){c.verbose("Destroying previous calendar for",H),w.removeData(M),c.unbind.events()},setup:{popup:function(){if(!f.inline&&(T.length||(T=w.children().first(),T.length))){if(e.fn.popup===n)return void c.error(b.popup);k.length||(k=e("<div/>").addClass(m.popup).prependTo(T.parent())),k.addClass(m.calendar);var t=f.onVisible,a=f.onHidden;x.length||(k.attr("tabindex","0"),t=function(){return c.focus(),f.onVisible.apply(k,arguments)},a=function(){return c.blur(),f.onHidden.apply(k,arguments)});var r=function(){return c.set.focusDate(c.get.date()),c.set.mode(f.startMode),f.onShow.apply(k,arguments)},o=f.on||(x.length?"focus":"click"),i=e.extend({},f.popupOptions,{popup:k,on:o,hoverable:"hover"===o,onShow:r,onVisible:t,onHide:f.onHide,onHidden:a});c.popup(i)}},inline:function(){(!T.length||f.inline)&&(k=e("<div/>").addClass(m.calendar).appendTo(w),x.length||k.attr("tabindex","0"))},input:function(){f.touchReadonly&&x.length&&o&&x.prop("readonly",!0)},date:function(){if(x.length){var e=x.val(),t=v.date(e,f);c.set.date(t,f.formatInput,!1)}}},create:{calendar:function(){var t,a,n,r,o,i=c.get.mode(),l=new Date,u=c.get.date(),s=c.get.focusDate(),d=s||u||f.initialDate||l;d=c.helper.dateInRange(d),s||(s=d,c.set.focusDate(s,!1,!1));var p=d.getMinutes(),g=d.getHours(),h=d.getDate(),v=d.getMonth(),b=d.getFullYear(),C="year"===i,M="month"===i,w="day"===i,x="hour"===i,T="minute"===i,H="time"===f.type,I=w?7:x?4:3,N=7===I?"seven":4===I?"four":"three",F=w||x?6:4,O=(new Date(b,v,1).getDay()-f.firstDayOfWeek%7+7)%7;if(!f.constantHeight&&w){var E=new Date(b,v+1,0).getDate()+O;F=Math.ceil(E/7)}var R=C?10:M?1:0,Y=w?1:0,A=x||T?1:0,S=x||T?h:1,V=new Date(b-R,v-Y,S-A,g),P=new Date(b+R,v+Y,S+A,g),j=C?new Date(10*Math.ceil(b/10)-9,0,0):M?new Date(b,0,0):w?new Date(b,v,0):new Date(b,v,h,-1),q=C?new Date(10*Math.ceil(b/10)+1,0,1):M?new Date(b+1,0,1):w?new Date(b,v+1,1):new Date(b,v,h+1),J=e("<table/>").addClass(m.table).addClass(N+" column").addClass(i);if(!H){var K=e("<thead/>").appendTo(J);r=e("<tr/>").appendTo(K),o=e("<th/>").attr("colspan",""+I).appendTo(r);var W=e("<span/>").addClass(m.link).appendTo(o);W.text(y.header(d,i,f));var z=M?f.disableYear?"day":"year":w?f.disableMonth?"year":"month":"day";W.data(D.mode,z);var L=e("<span/>").addClass(m.prev).appendTo(o);L.data(D.focusDate,V),L.toggleClass(m.disabledCell,!c.helper.isDateInRange(j,i)),e("<i/>").addClass(m.prevIcon).appendTo(L);var B=e("<span/>").addClass(m.next).appendTo(o);if(B.data(D.focusDate,P),B.toggleClass(m.disabledCell,!c.helper.isDateInRange(q,i)),e("<i/>").addClass(m.nextIcon).appendTo(B),w)for(r=e("<tr/>").appendTo(K),t=0;I>t;t++)o=e("<th/>").appendTo(r),o.text(y.dayColumnHeader((t+f.firstDayOfWeek)%7,f))}var U=e("<tbody/>").appendTo(J);for(t=C?10*Math.ceil(b/10)-9:w?1-O:0,a=0;F>a;a++)for(r=e("<tr/>").appendTo(U),n=0;I>n;n++,t++){var Q=C?new Date(t,v,1,g,p):M?new Date(b,t,1,g,p):w?new Date(b,v,t,g,p):x?new Date(b,v,h,t):new Date(b,v,h,g,5*t),Z=C?t:M?f.text.monthsShort[t]:w?Q.getDate():y.time(Q,f,!0);o=e("<td/>").addClass(m.cell).appendTo(r),o.text(Z),o.data(D.date,Q);var G=w&&Q.getMonth()!==v||!c.helper.isDateInRange(Q,i),X=c.helper.dateEqual(Q,u,i);o.toggleClass(m.disabledCell,G),o.toggleClass(m.activeCell,X),x||T||o.toggleClass(m.todayCell,c.helper.dateEqual(Q,l,i)),c.helper.dateEqual(Q,s,i)&&c.set.focusDate(Q,!1,!1)}if(f.today){var $=e("<tr/>").appendTo(U),_=e("<td/>").attr("colspan",""+I).addClass(m.today).appendTo($);_.text(y.today(f)),_.data(D.date,l)}c.update.focus(!1,J),k.empty(),J.appendTo(k)}},update:{focus:function(t,a){a=a||k;var n=c.get.mode(),r=c.get.date(),i=c.get.focusDate(),l=c.get.startDate(),u=c.get.endDate(),s=(t?i:null)||r||(o?null:i);a.find("td").each(function(){var t=e(this),a=t.data(D.date);if(a){var r=t.hasClass(m.disabledCell),d=t.hasClass(m.activeCell),p=c.helper.dateEqual(a,i,n),f=s?!!l&&c.helper.isDateInRange(a,n,l,s)||!!u&&c.helper.isDateInRange(a,n,s,u):!1;t.toggleClass(m.focusCell,p&&(!o||N)),t.toggleClass(m.rangeCell,f&&!d&&!r)}})}},refresh:function(){c.create.calendar()},bind:{events:function(){k.on("mousedown"+C,c.event.mousedown),k.on("touchstart"+C,c.event.mousedown),k.on("mouseup"+C,c.event.mouseup),k.on("touchend"+C,c.event.mouseup),k.on("mouseover"+C,c.event.mouseover),x.length?(x.on("input"+C,c.event.inputChange),x.on("focus"+C,c.event.inputFocus),x.on("blur"+C,c.event.inputBlur),x.on("click"+C,c.event.inputClick),x.on("keydown"+C,c.event.keydown)):k.on("keydown"+C,c.event.keydown)}},unbind:{events:function(){k.off(C),x.length&&x.off(C)}},event:{mouseover:function(t){var a=e(t.target),n=a.data(D.date),r=1===t.buttons;n&&c.set.focusDate(n,!1,!0,r)},mousedown:function(t){x.length&&t.preventDefault(),N=t.type.indexOf("touch")>=0;var a=e(t.target),n=a.data(D.date);n&&c.set.focusDate(n,!1,!0,!0)},mouseup:function(t){c.focus(),t.preventDefault(),t.stopPropagation(),N=!1;var a=e(t.target),n=a.parent();(n.data(D.date)||n.data(D.focusDate)||n.data(D.mode))&&(a=n);var r=a.data(D.date),o=a.data(D.focusDate),i=a.data(D.mode);if(r){var l=a.hasClass(m.today);c.selectDate(r,l)}else o?c.set.focusDate(o):i&&c.set.mode(i)},keydown:function(e){if((27===e.keyCode||9===e.keyCode)&&c.popup("hide"),c.popup("is visible"))if(37===e.keyCode||38===e.keyCode||39===e.keyCode||40===e.keyCode){var t=c.get.mode(),a="day"===t?7:"hour"===t?4:3,n=37===e.keyCode?-1:38===e.keyCode?-a:39==e.keyCode?1:a;n*="minute"===t?5:1;var r=c.get.focusDate()||c.get.date()||new Date,o=r.getFullYear()+("year"===t?n:0),i=r.getMonth()+("month"===t?n:0),l=r.getDate()+("day"===t?n:0),u=r.getHours()+("hour"===t?n:0),s=r.getMinutes()+("minute"===t?n:0),d=new Date(o,i,l,u,s);"time"===f.type&&(d=c.helper.mergeDateTime(r,d)),c.helper.isDateInRange(d,t)&&c.set.focusDate(d)}else if(13===e.keyCode){var p=c.get.focusDate();p&&c.selectDate(p)}(38===e.keyCode||40===e.keyCode)&&(e.preventDefault(),c.popup("show"))},inputChange:function(){var e=x.val(),t=v.date(e,f);c.set.date(t,!1)},inputFocus:function(){k.addClass(m.active)},inputBlur:function(){if(k.removeClass(m.active),f.formatInput){var e=c.get.date(),t=y.datetime(e,f);x.val(t)}},inputClick:function(){c.popup("show")}},get:{date:function(){return w.data(D.date)||null},focusDate:function(){return w.data(D.focusDate)||null},startDate:function(){var e=c.get.calendarModule(f.startCalendar);return(e?e.get.date():w.data(D.startDate))||null},endDate:function(){var e=c.get.calendarModule(f.endCalendar);return(e?e.get.date():w.data(D.endDate))||null},mode:function(){var t=w.data(D.mode)||f.startMode,a=c.get.validModes();return e.inArray(t,a)>=0?t:"time"===f.type?"hour":"month"===f.type?"month":"year"===f.type?"year":"day"},validModes:function(){var e=[];return"time"!==f.type&&(f.disableYear&&"year"!==f.type||e.push("year"),(!f.disableMonth&&"year"!==f.type||"month"===f.type)&&e.push("month"),f.type.indexOf("date")>=0&&e.push("day")),f.type.indexOf("time")>=0&&(e.push("hour"),f.disableMinute||e.push("minute")),e},isTouch:function(){try{return a.createEvent("TouchEvent"),!0}catch(e){return!1}},calendarModule:function(t){return t?(t instanceof e||(t=w.parent().children(t).first()),t.data(M)):null}},set:{date:function(e,t,a){t=t!==!1,a=a!==!1,e=c.helper.sanitiseDate(e),e=c.helper.dateInRange(e);var r=y.datetime(e,f);if(a&&f.onChange.call(H,e,r)===!1)return!1;var o=c.get.endDate();o&&e&&e>o&&c.set.endDate(n),c.set.dataKeyValue(D.date,e),c.set.focusDate(e),t&&x.length&&x.val(r)},startDate:function(e,t){e=c.helper.sanitiseDate(e);var a=c.get.calendarModule(f.startCalendar);a&&a.set.date(e),c.set.dataKeyValue(D.startDate,e,t)},endDate:function(e,t){e=c.helper.sanitiseDate(e);var a=c.get.calendarModule(f.endCalendar);a&&a.set.date(e),c.set.dataKeyValue(D.endDate,e,t)},focusDate:function(e,t,a,n){e=c.helper.sanitiseDate(e),e=c.helper.dateInRange(e);var r=c.set.dataKeyValue(D.focusDate,e,t);a=a!==!1&&r&&t===!1||F!=n,F=n,a&&c.update.focus(n)},mode:function(e,t){c.set.dataKeyValue(D.mode,e,t)},dataKeyValue:function(e,t,a){var n=w.data(e),r=n===t||t>=n&&n>=t;return t?w.data(e,t):w.removeData(e),a=a!==!1&&!r,a&&c.create.calendar(),!r}},selectDate:function(e,t){var a=c.get.mode(),n=t||"minute"===a||f.disableMinute&&"hour"===a||"date"===f.type&&"day"===a||"month"===f.type&&"month"===a||"year"===f.type&&"year"===a;if(n){var r=c.set.date(e)===!1;if(!r&&f.closable){c.popup("hide");var o=c.get.calendarModule(f.endCalendar);o&&(o.popup("show"),o.focus())}}else{var i="year"===a?f.disableMonth?"day":"month":"month"===a?"day":"day"===a?"hour":"minute";c.set.mode(i),"hour"===a||"day"===a&&c.get.date()?c.set.date(e):c.set.focusDate(e)}},changeDate:function(e){c.set.date(e)},clear:function(){c.set.date(n)},popup:function(){return T.popup.apply(T,arguments)},focus:function(){x.length?x.focus():k.focus()},blur:function(){x.length?x.blur():k.blur()},helper:{sanitiseDate:function(e){return e?(e instanceof Date||(e=v.date(""+e)),isNaN(e.getTime())?n:e):n},dateDiff:function(e,t,a){a=a||"day";var n="time"===f.type,r="year"===a,o=r||"month"===a,i="minute"===a,l=i||"hour"===a;return e=new Date(n?2e3:e.getFullYear(),n?0:r?0:e.getMonth(),n?1:o?1:e.getDate(),l?e.getHours():0,i?Math.floor(e.getMinutes()/5):0),t=new Date(n?2e3:t.getFullYear(),n?0:r?0:t.getMonth(),n?1:o?1:t.getDate(),l?t.getHours():0,i?Math.floor(t.getMinutes()/5):0),t.getTime()-e.getTime()},dateEqual:function(e,t,a){return!!e&&!!t&&0===c.helper.dateDiff(e,t,a)},isDateInRange:function(e,t,a,n){if(!a&&!n){var r=c.get.startDate();a=r&&f.minDate?Math.max(r,f.minDate):r||f.minDate,n=f.maxDate}return!(!e||a&&c.helper.dateDiff(e,a,t)>0||n&&c.helper.dateDiff(n,e,t)>0)},dateInRange:function(e,t,a){if(!t&&!a){var n=c.get.startDate();t=n&&f.minDate?Math.max(n,f.minDate):n||f.minDate,a=f.maxDate}var r="time"===f.type;return e?t&&c.helper.dateDiff(e,t,"minute")>0?r?c.helper.mergeDateTime(e,t):t:a&&c.helper.dateDiff(a,e,"minute")>0?r?c.helper.mergeDateTime(e,a):a:e:e},mergeDateTime:function(e,t){return e&&t?new Date(e.getFullYear(),e.getMonth(),e.getDate(),t.getHours(),t.getMinutes()):t}},setting:function(t,a){if(c.debug("Changing setting",t,a),e.isPlainObject(t))e.extend(!0,f,t);else{if(a===n)return f[t];f[t]=a}},internal:function(t,a){if(e.isPlainObject(t))e.extend(!0,c,t);else{if(a===n)return c[t];c[t]=a}},debug:function(){f.debug&&(f.performance?c.performance.log(arguments):(c.debug=Function.prototype.bind.call(console.info,console,f.name+":"),c.debug.apply(console,arguments)))},verbose:function(){f.verbose&&f.debug&&(f.performance?c.performance.log(arguments):(c.verbose=Function.prototype.bind.call(console.info,console,f.name+":"),c.verbose.apply(console,arguments)))},error:function(){c.error=Function.prototype.bind.call(console.error,console,f.name+":"),c.error.apply(console,arguments)},performance:{log:function(e){var t,a,n;f.performance&&(t=(new Date).getTime(),n=l||t,a=t-n,l=t,u.push({Name:e[0],Arguments:[].slice.call(e,1)||"",Element:H,"Execution Time":a})),clearTimeout(c.performance.timer),c.performance.timer=setTimeout(c.performance.display,500)},display:function(){var t=f.name+":",a=0;l=!1,clearTimeout(c.performance.timer),e.each(u,function(e,t){a+=t["Execution Time"]}),t+=" "+a+"ms",i&&(t+=" '"+i+"'"),(console.group!==n||console.table!==n)&&u.length>0&&(console.groupCollapsed(t),console.table?console.table(u):e.each(u,function(e,t){console.log(t.Name+": "+t["Execution Time"]+"ms")}),console.groupEnd()),u=[]}},invoke:function(t,a,o){var i,l,u,s=I;return a=a||p,o=H||o,"string"==typeof t&&s!==n&&(t=t.split(/[\. ]/),i=t.length-1,e.each(t,function(a,r){var o=a!=i?r+t[a+1].charAt(0).toUpperCase()+t[a+1].slice(1):t;if(e.isPlainObject(s[o])&&a!=i)s=s[o];else{if(s[o]!==n)return l=s[o],!1;if(!e.isPlainObject(s[r])||a==i)return s[r]!==n?(l=s[r],!1):(c.error(b.method,t),!1);s=s[r]}})),e.isFunction(l)?u=l.apply(o,a):l!==n&&(u=l),e.isArray(r)?r.push(u):r!==n?r=[r,u]:u!==n&&(r=u),l}},d?(I===n&&c.initialize(),c.invoke(s)):(I!==n&&I.invoke("destroy"),c.initialize())}),r!==n?r:o},e.fn.calendar.settings={name:"Calendar",namespace:"calendar",debug:!1,verbose:!1,performance:!1,type:"datetime",firstDayOfWeek:0,constantHeight:!0,today:!1,closable:!0,monthFirst:!0,touchReadonly:!0,inline:!1,on:null,initialDate:null,startMode:!1,minDate:null,maxDate:null,ampm:!0,disableYear:!1,disableMonth:!1,disableMinute:!1,formatInput:!0,startCalendar:null,endCalendar:null,popupOptions:{position:"bottom left",lastResort:"bottom left",prefer:"opposite",hideOnScroll:!1},text:{days:["S","M","T","W","T","F","S"],months:["January","February","March","April","May","June","July","August","September","October","November","December"],monthsShort:["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"],today:"Today",now:"Now",am:"AM",pm:"PM"},formatter:{header:function(e,t,a){return"year"===t?a.formatter.yearHeader(e,a):"month"===t?a.formatter.monthHeader(e,a):"day"===t?a.formatter.dayHeader(e,a):"hour"===t?a.formatter.hourHeader(e,a):a.formatter.minuteHeader(e,a)},yearHeader:function(e,t){var a=10*Math.ceil(e.getFullYear()/10);return a-9+" - "+(a+2)},monthHeader:function(e,t){return e.getFullYear()},dayHeader:function(e,t){var a=t.text.months[e.getMonth()],n=e.getFullYear();return a+" "+n},hourHeader:function(e,t){return t.formatter.date(e,t)},minuteHeader:function(e,t){return t.formatter.date(e,t)},dayColumnHeader:function(e,t){return t.text.days[e]},datetime:function(e,t){if(!e)return"";var a="time"===t.type?"":t.formatter.date(e,t),n=t.type.indexOf("time")<0?"":t.formatter.time(e,t,!1),r="datetime"===t.type?" ":"";return a+r+n},date:function(e,t){if(!e)return"";var a=e.getDate(),n=t.text.months[e.getMonth()],r=e.getFullYear();return"year"===t.type?r:"month"===t.type?n+" "+r:(t.monthFirst?n+" "+a:a+" "+n)+", "+r},time:function(e,t,a){if(!e)return"";var n=e.getHours(),r=e.getMinutes(),o="";return t.ampm&&(o=" "+(12>n?t.text.am:t.text.pm),n=0===n?12:n>12?n-12:n),n+":"+(10>r?"0":"")+r+o},today:function(e){return"date"===e.type?e.text.today:e.text.now}},parser:{date:function(t,a){if(!t)return null;if(t=(""+t).trim().toLowerCase(),0===t.length)return null;var r,o,i,l=-1,u=-1,s=-1,d=-1,p=-1,c=n,f="time"===a.type,m=a.type.indexOf("time")<0,g=t.split(a.regExp.dateWords),h=t.split(a.regExp.dateNumbers);if(!m)for(c=e.inArray(a.text.am.toLowerCase(),g)>=0?!0:e.inArray(a.text.pm.toLowerCase(),g)>=0?!1:n,r=0;r<h.length;r++){var y=h[r];if(y.indexOf(":")>=0){if(0>u||0>l){var v=y.split(":");for(i=0;i<Math.min(2,v.length);i++)o=parseInt(v[i]),isNaN(o)&&(o=0),0===i?u=o%24:l=o%60}h.splice(r,1)}}if(!f){for(r=0;r<g.length;r++){var D=g[r];if(!(D.length<=0)){for(D=D.substring(0,Math.min(D.length,3)),o=0;o<a.text.months.length;o++){var b=a.text.months[o];if(b=b.substring(0,Math.min(D.length,Math.min(b.length,3))).toLowerCase(),b===D){d=o+1;break}}if(d>=0)break}}for(r=0;r<h.length;r++)if(o=parseInt(h[r]),!isNaN(o)&&o>59){p=o,h.splice(r,1);break}if(0>d)for(r=0;r<h.length;r++)if(i=r>1||a.monthFirst?r:1===r?0:1,o=parseInt(h[i]),!isNaN(o)&&o>=1&&12>=o){d=o,h.splice(i,1);break}for(r=0;r<h.length;r++)if(o=parseInt(h[r]),!isNaN(o)&&o>=1&&31>=o){s=o,h.splice(r,1);break}if(0>p)for(r=h.length-1;r>=0;r--)if(o=parseInt(h[r]),!isNaN(o)){99>o&&(o+=2e3),p=o,h.splice(r,1);break}}if(!m){if(0>u)for(r=0;r<h.length;r++)if(o=parseInt(h[r]),!isNaN(o)&&o>=0&&23>=o){u=o,h.splice(r,1);break}if(0>l)for(r=0;r<h.length;r++)if(o=parseInt(h[r]),!isNaN(o)&&o>=0&&59>=o){l=o,h.splice(r,1);break}}if(0>l&&0>u&&0>s&&0>d&&0>p)return null;0>l&&(l=0),0>u&&(u=0),0>s&&(s=1),0>d&&(d=1),0>p&&(p=(new Date).getFullYear()),c!==n&&(c?12===u&&(u=0):12>u&&(u+=12));var C=new Date(p,d-1,s,u,l);return(C.getMonth()!==d-1||C.getFullYear()!==p)&&(C=new Date(p,d,0,u,l)),isNaN(C.getTime())?null:C}},onChange:function(e,t){return!0},onShow:function(){},onVisible:function(){},onHide:function(){},onHidden:function(){},selector:{popup:".ui.popup",input:"input",activator:"input"},regExp:{dateWords:/[^A-Za-z\u00C0-\u024F]+/g,dateNumbers:/[^\d:]+/g},error:{popup:"UI Popup, a required component is not included in this page",method:"The method you called is not defined."},className:{calendar:"calendar",active:"active",popup:"ui popup",table:"ui celled center aligned unstackable table",prev:"prev link",next:"next link",prevIcon:"chevron left icon",nextIcon:"chevron right icon",link:"link",cell:"link",disabledCell:"disabled",activeCell:"active",rangeCell:"range",focusCell:"focus",todayCell:"today",today:"today link"},metadata:{date:"date",focusDate:"focusDate",startDate:"startDate",endDate:"endDate",mode:"mode"}}}(jQuery,window,document);

$(function() {

    // Javascript of the sous-chef application.
    // **************************************

    $('.ui.open-menu').on('click', function() {
        $('.ui.sidebar').sidebar('toggle');
    });

    $('.help-text').popup();

    $('.message .close').on('click', function() {
        $(this).closest('.message').transition('fade');
    });

    $('.ui.accordion').accordion();
    $('.ui.dropdown').dropdown({transition: 'drop'});

    $('table').tablesort();

    $('.ui.calendar').calendar({
        type: 'date',
        formatter: {
            date: function (date, settings) {
                if (!date) return '';
                var day = date.getDate();
                var month = date.getMonth() + 1;
                var year = date.getFullYear();
                if (month < 10) month = '0' + month;
                if (day < 10) day = '0' + day;
                return year + '-' + month + '-' + day;
            }
        }
    });

});

$(function() {
    // Javascript of the delivery application
    // ****************************************

    $('.ui.dropdown.maindish.selection').dropdown('setting', 'onChange', function(value, text, $selectedItem) {
        $url = $(".field.dish.selection").data('url');
        window.location.replace($url+value);
    });

});

$(function() {

    // Javascript of the member application.
    // **************************************

    $('.ui.dropdown.member.status > .menu > .item').click(function () {
        var value = $(this).data('value');
        var today = new Date();
        var modalCtntURL = $('.ui.dropdown.status').attr('data-url');
        $.get(modalCtntURL, {status:value}, function(data, modalCtntURL){
            $('.ui.modal.status').html(data).modal("setting", {
                closable: false,
                // Inside modal init
                onVisible: function () {
                    // Enable status confirmation dropdown
                    $('.ui.status_to.dropdown').dropdown();
                    // Init dates field (start and end)
                    $('#rangestart').calendar({
                        type: 'date',
                        on: 'click',
                        minDate: new Date(
                            today.getFullYear(),
                            today.getMonth(),
                            today.getDate()),
                        formatter: {
                            date: function (date, settings) {
                                if (!date) return '';
                                var day = date.getDate();
                                var month = date.getMonth() + 1;
                                var year = date.getFullYear();
                                if (month < 10) month = '0' + month;
                                if (day < 10) day = '0' + day;
                                return year + '-' + month + '-' + day;
                            }
                        },
                        endCalendar: $('#rangeend'),
                    });
                    $('#rangeend').calendar({
                        type: 'date',
                        formatter: {
                            date: function (date, settings) {
                                if (!date) return '';
                                var day = date.getDate();
                                var month = date.getMonth() + 1;
                                var year = date.getFullYear();
                                if (month < 10) month = '0' + month;
                                if (day < 10) day = '0' + day;
                                return year + '-' + month + '-' + day;
                            }
                        },
                        startCalendar: $('#rangestart'),
                    });
                },
                // When approvind modal, submit form
                onApprove: function($element, modalCtntURL) {
                    $.ajax({
                         type: 'POST',
                         url: $('.ui.dropdown.status').attr('data-url'),
                         data: $('#change-status-form').serialize(),
                         success: function (xhr, ajaxOptions, thrownError) {
                             if ( $(xhr).find('.errorlist').length > 0 ) {
                                 $('.ui.modal.status').html(xhr);
                                 console.log('show modal..')
                                 $('.ui.modal.status').modal("show");
                             } else {
                                 location.reload();
                             }
                         },
                     });
                },
                // When denying modal, restore default value for status dropdown
                onDeny: function($element) {
                    $('.ui.dropdown.status').dropdown('restore defaults');
                }
            }).modal("show");
        });
    });

    if($('#dietary_restriction-delivery_type select').val() == 'E') {
        $('#form-meals-schedule').hide();
        hideUiAccordionDays();
    } else {
        $('#form-meals-schedule').show();
        showUiAccordionSelectedDays();
    }

    $('#dietary_restriction-delivery_type .dropdown').dropdown(
        'setting', 'onChange', function(value, text, $selectedItem) {
            if($selectedItem.data('value') == 'E') {
                $('#form-meals-schedule').hide();
                hideUiAccordionDays();
            } else {
                $('#form-meals-schedule').show();
                showUiAccordionSelectedDays();
            }
        }
    );

    var same_as_client = $('#id_payment_information-same_as_client');
    // Initial state
    if (same_as_client && same_as_client.checked) {
        $('#billing_select_member').hide();
    }
    $("#id_payment_information-same_as_client").on("change", function() {
        if (this.checked) {
            $('#billing_select_member').hide();
        } else {
            $('#billing_select_member').show();
        }
    });

    $('.ui.button.add.member').on('click', function() {
        $('.existing--member').val('').attr('disabled', 'disabled');
        $(this).transition('scale');
        $('.ui.add.form.member').transition('scale');
    });

    $('.ui.button.cancel.add.member').on('click', function() {
        $('.ui.button.add.member').transition('scale');
        $('.existing--member').removeAttr('disabled');
    });

    if( $('.firstname').val() !== '' || $('.lastname').val() !== ''
        && $('.existing--member').val() === '' ) {
        $('.ui.button.add.member').transition('scale');
        $('.existing--member').attr('disabled', 'disabled');
        $('.ui.add.form.member').transition('scale');
    }

    $search_url = $('.ui.search').attr('data-url')
    $('.ui.search').search({
        apiSettings: {
            cache : 'local',
            url: $search_url + '?name={query}',
        },
        minCharacters : 3,
    });

    function showOneAccordionElement(element, index, array) {
        selector = '.ui.accordion.meals.' + element;
        $(selector).show();
    }
    function showUiAccordionSelectedDays() {
        var $selected = $("#form-meals-schedule select[multiple='multiple']").val();
        if ($selected) {
          $selected.forEach(showOneAccordionElement);
        }
    }
    function hideUiAccordionDays() {
        $('.ui.accordion.meals').each(function () {
          $(this).hide();
        });
    }

    $("#form-meals-schedule select[multiple='multiple']").change(function () {
        hideUiAccordionDays();
        showUiAccordionSelectedDays();
    });
    hideUiAccordionDays();
    showUiAccordionSelectedDays();

});

$(function() {

    // Javascript of the order application.
    // **************************************

    $('.order-delete').click(function(){
        var order_id = $(this).attr('data-order-id');
        var selector = '.ui.basic.modal.order-' + order_id;
        $(selector).modal('show');
    });

    $('.ui.dropdown.order.status .menu > .item').click(function () {
        $('.ui.dropdown.order.status').addClass('loading');
        $.ajax({
            url: $('.ui.dropdown.order.status').attr('data-url'),
            type: "POST",
            data: {
                'status': $(this).data('value'),
                'csrfmiddlewaretoken': $('.ui.dropdown.order.status').attr('data-csrf-token'),
            },
            success: function(response) {
                $('.ui.dropdown.order.status').removeClass('loading');
            }
        });
    });
});

$(function() {
    // Javascript of the billing application
    // ****************************************

    $('.billing-delete').click(function(){
        var billing_id = $(this).attr('data-billing-id');
        var selector = '.ui.basic.modal.billing-' + billing_id;
        $(selector).modal('show');
    });

    $('#billing_delivery_date').calendar({
        type: 'month',
        formatter: {
            date: function (date, settings) {
                if (!date) return '';
                var month = date.getMonth() + 1;
                var year = date.getFullYear();
                if (month < 10) month = '0' + month;
                return year + '-' + month ;
            }
        }
    });

    $('.add.icon').popup();
});
$(function() {

    // Javascript of the page application.
    // **************************************

    $('.ui.large.form').form({
        on: 'submit',
        revalidate: 'false',
        fields: {
            username: {
                identifier: 'username',
                rules: [{
                    type   : 'empty',
                    prompt : 'Please enter a username'
                }]
            },
            password: {
                identifier: 'password',
                rules: [{
                    type   : 'empty',
                    prompt : 'Please enter a password'
                    },{
                    type   : 'minLength[6]',
                    prompt : 'Your password must be at least {ruleValue} characters'
                }]
            }
        }
    })
});
