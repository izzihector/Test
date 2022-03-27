ProbationBreadCrumb = {
    props:['state'],
    data() {
        return {
            states: {              
                'objective_setting': 'Objective Setting',
                'probation_period': 'Probation Period',
                'self_assessment': 'Self Assessment',
                'supervisor_assessment': 'Supervisor Assessment',
                'final_comments': 'Final Comments',
                'done': 'Done',
                'cancel': 'Cancel'
            }
        }
    },
    template: `
        <div class="custom_portal_breadcrumb flat">
            <template v-for="(name, key, index) in states" :key="index">
                <a href="#" @click.prevent="" :class="{active: key==state}">{{name}}</a>
            </template>
        </div>
    `
}