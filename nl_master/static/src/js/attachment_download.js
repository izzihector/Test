odoo.define('nl_master.attachment_download', function (require) {
    "use strict";

    /**
     * +-------------+-------------------------------------- ---------------+
     * | Sr No. |                   Functionality                           |
     * +-------------+------------------------------------------------------+
     * |   1    | context = {download_file:True}, then download that file   |
     * |        |(click on open attachment icon)                            |
     * +-------------+------------------------------------------------------+
     */

    var ActionManager = require('web.ActionManager');
    var basic_fields = require('web.basic_fields');
    var Context = require('web.Context');
    var Dialog = require('web.Dialog');
    var dom = require('web.dom');
    var field_utils = require('web.field_utils');
    var pyUtils = require('web.py_utils');
    var utils = require('web.utils');

    basic_fields.FieldBinaryFile.include({
        _renderReadonly: function () {
            this._super();
            if (this.value) {
                var size = field_utils.format['binary'](this.value, this.field, {});
                this.$el.append(" (" + size + ")");
            }
        },
    });

    ActionManager.include({
        _onExecuteAction: function (ev) {
            ev.stopPropagation();
            var self = this;
            var actionData = ev.data.action_data;
            var env = ev.data.env;
            var context = new Context(env.context, actionData.context || {});
            var recordID = env.currentID || null; // pyUtils handles null value, not undefined
            var def;
            // determine the action to execute according to the actionData
            if (actionData.special) {
                def = Promise.resolve({
                    type: 'ir.actions.act_window_close',
                    infos: { special: true },
                });
            } else if (actionData.type === 'object') {
                // call a Python Object method, which may return an action to execute
                var args = recordID ? [[recordID]] : [env.resIDs];
                if (actionData.args) {
                    try {
                        // warning: quotes and double quotes problem due to json and xml clash
                        // maybe we should force escaping in xml or do a better parse of the args array
                        var additionalArgs = JSON.parse(actionData.args.replace(/'/g, '"'));
                        args = args.concat(additionalArgs);
                    } catch (e) {
                        console.error("Could not JSON.parse arguments", actionData.args);
                    }
                }
                def = this._rpc({
                    route: '/web/dataset/call_button',
                    params: {
                        args: args,
                        kwargs: {context: context.eval()},
                        method: actionData.name,
                        model: env.model,
                    },
                });
            } else if (actionData.type === 'action') {
                // execute a given action, so load it first
                def = this._loadAction(actionData.name, _.extend(pyUtils.eval('context', context), {
                    active_model: env.model,
                    active_ids: env.resIDs,
                    active_id: recordID,
                }));
            } else {
                def = Promise.reject();
            }
            // use the DropPrevious to prevent from executing the handler if another
            // request (doAction, switchView...) has been done meanwhile ; execute
            // the fail handler if the 'call_button' or 'loadAction' failed but not
            // if the request failed due to the DropPrevious,
            def.guardedCatch(ev.data.on_fail);
            this.dp.add(def).then(function (action) {
                // show effect if button have effect attribute
                // rainbowman can be displayed from two places: from attribute on a button or from python
                // code below handles the first case i.e 'effect' attribute on button.
                var effect = false;
                if(action && action.res_model){
                    if(_.contains(['employee.attendance.line','training.attendance.line'], action.res_model)){
                        sessionStorage.historyStatus = 'unchange';
                    }
                }
                if (actionData.effect) {
                    effect = pyUtils.py_eval(actionData.effect);
                }
                if (action && action.constructor === Object) {
                    // filter out context keys that are specific to the current action, because:
                    //  - wrong default_* and search_default_* values won't give the expected result
                    //  - wrong group_by values will fail and forbid rendering of the destination view
                    var ctx = new Context(
                        _.object(_.reject(_.pairs(env.context), function (pair) {
                            return pair[0].match('^(?:(?:default_|search_default_|show_).+|' +
                                                 '.+_view_ref|group_by|group_by_no_leaf|active_id|' +
                                                 'active_ids|orderedBy)$') !== null;
                        }))
                    );
                    ctx.add(actionData.context || {});
                    ctx.add({active_model: env.model});
                    if (recordID) {
                        ctx.add({
                            active_id: recordID,
                            active_ids: [recordID],
                        });
                    }
                    ctx.add(action.context || {});
                    action.context = ctx;
                    // in case an effect is returned from python and there is already an effect
                    // attribute on the button, the priority is given to the button attribute
                    action.effect = effect || action.effect;
                } else {
                    // if action doesn't return anything, but there is an effect
                    // attribute on the button, display rainbowman
                    action = {
                        effect: effect,
                        type: 'ir.actions.act_window_close',
                    };
                }
                var eval_context = pyUtils.eval('context', action.context);
                if(eval_context && eval_context.download_file){
                    var value = eval_context.default_download_attachment;
                    if(value){
                        $.blockUI();
                        self.getSession().get_file({
                            url: '/web/binary/custom_download_file',
                            data: {
                                data: JSON.stringify({
                                    model: env.model,
                                    id: recordID,
                                    field: env.model,
                                    filename_field: eval_context.default_download_filename,
                                    data: utils.is_bin_size(value) ? null : value,
                                    context: {}
                                })
                            },
                            complete: $.unblockUI,
                            error: (error) => self.call('crash_manager', 'rpc_error', error),
                            success: function(){
                                var options = {on_close: ev.data.on_closed};
                                action.flags = _.extend({}, action.flags, {searchPanelDefaultNoFilter: true});
                                return self.doAction(action, options).then(ev.data.on_success, ev.data.on_fail);
                            },
                        });
                    }
                }else{
                    var options = {on_close: ev.data.on_closed};
                    action.flags = _.extend({}, action.flags, {searchPanelDefaultNoFilter: true});
                    return self.doAction(action, options).then(ev.data.on_success, ev.data.on_fail);
                }
            });
        },

    });

});
