odoo.define("nl_contract.disable_drag_drop_kanban",function(require){

    var KanbanRenderer = require('web.KanbanRenderer');
    var viewUtils = require('web.viewUtils');

    var BasicView = require('web.BasicView');
    var session = require('web.session');
    BasicView.include({
            init: function(viewInfo, params) {
                var self = this;
                this._super.apply(this, arguments);
                var model = self.controllerParams.modelName in ['hr.employee','hr.contract'] ? 'True' : 'False';
                if(model) {
                    session.user_has_group('base.group_erp_manager').then(function(has_group) {
                        if(!has_group) {
                            self.controllerParams.archiveEnabled = 'False' in viewInfo.fields;
                        }
                    });
                }
            },
    });

    KanbanRenderer.include({
        _setState: function (state) {
            this.state = state;
            var self = this;

            var groupByField = state.groupedBy[0];
            var cleanGroupByField = this._cleanGroupByField(groupByField);
            var groupByFieldAttrs = state.fields[cleanGroupByField];
            var groupByFieldInfo = state.fieldsInfo.kanban[cleanGroupByField];
            // Deactivate the drag'n'drop if the groupedBy field:
            // - is a date or datetime since we group by month or
            // - is readonly (on the field attrs or in the view)
            var draggable = true;
            if (groupByFieldAttrs) {
                if (groupByFieldAttrs.type === "date" || groupByFieldAttrs.type === "datetime") {
                    draggable = false;
                } else if (groupByFieldAttrs.readonly !== undefined) {
                    draggable = !(groupByFieldAttrs.readonly);
                }
            }

            // Deactivate the drag & drop for hr.contract
            if(self.state.model == 'hr.contract'){
                draggable = false
            }
            if(self.state.model == 'hr.applicant'){
                draggable = true
            }

            if (groupByFieldInfo) {
                if (draggable && groupByFieldInfo.readonly !== undefined) {
                    draggable = !(groupByFieldInfo.readonly);
                }
            }
            this.groupedByM2O = groupByFieldAttrs && (groupByFieldAttrs.type === 'many2one');
            var relation = this.groupedByM2O && groupByFieldAttrs.relation;
            var groupByTooltip = groupByFieldInfo && groupByFieldInfo.options.group_by_tooltip;
            this.columnOptions = _.extend(this.columnOptions, {
                draggable: draggable,
                group_by_tooltip: groupByTooltip,
                groupedBy: groupByField,
                grouped_by_m2o: this.groupedByM2O,
                relation: relation,
                quick_create: this.quickCreateEnabled && viewUtils.isQuickCreateEnabled(state),
            });
            this.createColumnEnabled = this.groupedByM2O && this.columnOptions.group_creatable;
        },
	
    });

});
