BreadCrumb = {
    props:['state', 'appraisalType'],
    data() {
        return {
            states: {},
            adminStaffStates: {               
                'objective_setting': 'Objective Setting', 
                'performance_period': 'Performance Period', 
                'self_review': 'Self Assessment', 
                'supervisor_review': 'Supervisor Assessment', 
                '2nd_supervisor_review': '2nd Supervisor Assessment', 
                'final_comments': 'Final Comments', 
                'done': 'Done',
            },
            fieldStaffStates : {
                'supervisor_review': 'Supervisor Assessment', 
                'done': 'Done',
            },
            pipAppraisalStates : {
                'draft': 'Draft',
                'planning': 'Planning',
                'performance_period': 'Performance Period',
                'assessment': 'Assessment',
                'final_comments': 'Final Comments',
                'done': 'Done',
            }
        }
    },
    mounted() {
        if (this.appraisalType == 'fieldStaff') {
            this.states = this.fieldStaffStates
        } else if (this.appraisalType == 'adminStaff') {
            this.states = this.adminStaffStates
        } else {
            this.states = this.pipAppraisalStates
        }
    },
    template: `
        <div class="custom_portal_breadcrumb flat" v-if="states">
            <template v-for="(name, key, index) in states" :key="index">
                <a href="#" @click.prevent="" :class="{active: key==state}">{{name}}</a>
            </template>
        </div>
    `
}