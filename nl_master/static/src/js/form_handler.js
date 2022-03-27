odoo.define('nl_master.form_tree_handler', function (require) {
    "use strict";


    var FormRenderer = require('web.FormRenderer');
    var FormController = require('web.FormController');
    var FormView = require('web.FormView');
    var ListView = require('web.ListView');
    var ListController = require('web.ListController');
    var ListRenderer = require('web.ListRenderer');
    var session = require('web.session');
    var view_dialogs = require('web.view_dialogs')

    var is_finance_user = false
    session.user_has_group('nl_payroll.group_payroll_finance').then(function(has_group){
        is_finance_user = has_group
    });
    var is_admin_user = false
    session.user_has_group('hr_payroll.group_hr_payroll_manager').then(function(has_group){
        is_admin_user = has_group
    });
    var is_only_readonly = false
    session.user_has_group('nl_master.group_payroll_read_only').then(function(has_group){
        is_only_readonly = has_group
    });

    var myModels = ['generate.payroll.master', 'hr.payslip']
    var editableModels = ['hr.payslip']
    FormRenderer.include({
        init: function(parent, state, params) { 
            
            // Restrict fiance user from creating and editing for myModels list in form view.
            if(myModels.includes(state.model) && (is_finance_user === true || (is_only_readonly && !is_admin_user && !is_finance_user) )) {
                params.activeActions.create = false
                if (!editableModels.includes(state.model)) {
                    params.activeActions.edit = false    
                }
            }

            if (state.model == 'hr.payslip') {
                // Do not allow admin users to edit hr payslip in finance review stage
                if (state.evalContext.state === 'finance' && is_admin_user == true && is_finance_user === false ) {
                    params.activeActions.edit = false
                }

                // Do not allow finance users to edit hr payslips in hr stage
                if (state.evalContext.state === 'hr' && is_finance_user === true ) {
                    params.activeActions.edit = false
                }
            }

            // Allow editing employee.absent and manual.allowance deduction models for hr admin in hr stage and for finance in finance stage. form view
            if (['employee.absent', 'manual.allowance.deduction'].includes(state.model)) {
                var current_user = false
                if (is_finance_user === true) {
                    current_user = 'finance'
                }else if(is_admin_user === true) {
                    current_user = 'admin'
                }
                if (current_user != false) {
                    if ((state.evalContext.parent_state === 'hr' && current_user == 'finance') | (state.evalContext.parent_state === 'finance' && current_user == 'admin') | ['hr', 'finance', 'draft'].indexOf(state.evalContext.parent_state) === -1 ) {
                        params.activeActions.create = false
                        params.activeActions.edit = false
                    } 
                }
            }       

            this._super.apply(this, arguments);
        },
    });
    ListRenderer.include({
        init: function(parent, state, params) { 

            if(myModels.includes(state.model) && is_finance_user === true) {
                params.activeActions.create = false
                params.activeActions.edit = false
            }

            // Allow editing employee.absent and manual.allowance deduction models for hr admin in hr stage and for finance in finance stage. tree view
            if (['employee.absent', 'manual.allowance.deduction'].includes(state.model)) {
                var current_user = false
                if (is_finance_user === true) {
                    current_user = 'finance'
                }else if(is_admin_user === true) {
                    current_user = 'admin'
                }

                if (current_user != false) {
                    var parent_state = ''
                    if (state.data.length > 0) {
                        parent_state = state.data[0].data.parent_state
                    } else {
                        parent_state = state.context.parent_state
                    }
                    if ((parent_state === 'hr' && current_user == 'finance') | (parent_state === 'finance' && current_user == 'admin') | ['hr', 'finance', 'draft'].indexOf(parent_state) === -1 ) {
                        params.activeActions.create = false
                        params.activeActions.edit = false
                        params.editable = false
                    } 
                }
            }       
            this._super.apply(this, arguments);
        },
    });

    
});



        // FormView.include({
    //     init: function(viewInfo, params){
    //         var self = this;
    //         this._super.apply(this, arguments);
    //         // Restrict fiance user from creating and editing for myModels list in form view.
    //         if(myModels.includes(this.loadParams.modelName) && is_finance_user === true) {
    //             this.controllerParams.activeActions.create = false
    //             if (!editableModels.includes(this.loadParams.modelName)) {
    //                 this.controllerParams.activeActions.edit = false    
    //             }
    //         }
    //     }
    // });


        // ListView.include({
    //     init: function(viewInfo, params){
    //         var self = this;
    //         this._super.apply(this, arguments);
    //         // Restrict fiance user from creating and editing for myModels list in tree view.
    //         if(myModels.includes(this.loadParams.modelName) && is_finance_user === true) {
    //             this.controllerParams.activeActions.create = false
    //             this.controllerParams.activeActions.edit = false
    //         }
    //     }
    // });


    // FormController.include({
    //     _onOpenRecord: function(ev) {
    //         ev.stopPropagation();
    //         var record = this.model.get(ev.data.id, {raw: true});
    //         console.log("open record treeeeeee cladded>>>>>>>>>>>>>>>>", ev.data, ev.data.mode)
    //         console.log(record)
    //         console.log(ev)
    //         console.log(this)
    //         ev.target.activeActions.edit = false
    //         this.trigger_up('switch_view', {
    //             view_type: 'form',
    //             res_id: record.res_id,
    //             mode: ev.data.mode || 'readonly',
    //             model: this.modelName,
    //             activeActions: {
    //                 edit: false
    //             }
    //         });
    //     },
    // });
    // ListController.include({
    //     _onOpenRecord: function(ev) {
    //         ev.stopPropagation();
    //         var record = this.model.get(ev.data.id, {raw: true});
    //         console.log("open record treeeeeee cladded>>>>>>>>>>>>>>>>", ev.data, ev.data.mode)
    //         console.log(record)
    //         console.log(ev)
    //         console.log(this)
    //         ev.target.activeActions.edit = false
    //         this.trigger_up('switch_view', {
    //             view_type: 'form',
    //             res_id: record.res_id,
    //             mode: ev.data.mode || 'readonly',
    //             model: this.modelName,
    //             activeActions: {
    //                 edit: false
    //             }
    //         });
    //     },
    // });