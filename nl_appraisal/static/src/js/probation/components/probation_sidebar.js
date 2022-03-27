ProbationSideBarComponent = {
    props: {
        sideBarType: {
            default: 'employees'
        },
        accessData: {}
    },
    emits: ['change_component'],
    inject: ['currentComponent', 'appraisalData'],
    data() {
        return {
            style: {
                activeColor: 'white',
                activeBg: '#875A7B',
                color: '#999',
                bg: '#ebebeb'
            }
        }
    },
    template: `
        <template v-if="sideBarType == 'employees'">
            <template v-if="'probation_period'==accessData.state">
                <div   class="d-flex align-items-center" style="cursor: pointer;">
                    <div
                        class="font-weight-bold" style="width: 40px; height: 40px; display: flex; justify-content: center; align-items: center; border-radius: 20px;">
                        <span class="fa-fa-check" v-if="appraisalData.value.metaInfo.general_objective_feed_state"> <i class="fa fa-check"/> </span>
                                <span v-else="">1</span>
                    </div>
                    <span class="ml-3"
                        style="color: #656565;">Probation Period Objectives</span>
                </div>
            </template>

            <template v-if="'self_assessment'==accessData.state">
                <div @click="$emit('change_component', 'ProbationSelfAssessment')"  class="d-flex align-items-center" style="cursor: pointer;">
                    <div :style="{color: currentComponent.value == 'ProbationSelfAssessment'? style.activeColor : style.color, background: currentComponent.value=='ProbationSelfAssessment' ? style.activeBg : style.bg}"
                        class="font-weight-bold" style="width: 40px; height: 40px; display: flex; justify-content: center; align-items: center; border-radius: 20px;">
                        <span class="fa-fa-check" v-if="appraisalData.value.metaInfo.setting_self_assessment_state"> <i class="fa fa-check"/> </span>
                                <span v-else="">1</span>
                    </div>
                    <span class="ml-3" :class="{'font-weight-bold': currentComponent.value=='ProbationSelfAssessment'}"
                        style="color: #656565;">Employee Assessment</span>
                </div>
            </template>

            <template v-if="accessData.state == 'self_assessment'">
                <div style="margin-left:19px; width:2px; height:30px; background:#ebebeb" class="my-1"></div>
                <div @click="$emit('change_component', 'ProbationSubmitForm')"  class="d-flex align-items-center" style="cursor: pointer;">
                    <div :style="{color: currentComponent.value == 'ProbationSubmitForm'? style.activeColor : style.color, background: currentComponent.value=='ProbationSubmitForm' ? style.activeBg : style.bg}"
                        class="font-weight-bold"
                        style="width: 40px; height: 40px; display: flex; justify-content: center; align-items: center; border-radius: 20px;">
                        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" style="width:1.4rem"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 5l7 7-7 7M5 5l7 7-7 7"></path></svg>
                    </div>
                    <span class="ml-3" :class="{'font-weight-bold': currentComponent.value=='ProbationSubmitForm'}" style="color: #656565;">Validate and Submit</span>
                </div>
            </template>

        </template>

        <template v-if="sideBarType == 'managers'">
            <div v-if="['supervisor_assessment'].includes(accessData.state) && currentComponent.value != 'ProbationStateReturner'" class="position-absolute text-center text-sm fixed-bottom mb-4">
                <small @click="$emit('change_component','ProbationStateReturner')" class="btn btn-secondary btn-sm btn-odoo">Move back to Self Assessment</small>
            </div>
            <div v-if="currentComponent.value=='ProbationStateReturner'" @click="$emit('change_component', accessData.state=='final_comments' ? 'ProbationFullForm': 'SupervisorAssessment')"  class="d-flex align-items-center" style="cursor: pointer;">
                <div style="color: #999; background: #ebebeb" class="font-weight-bold"
                    style="width: 40px; height: 40px; display: flex; justify-content: center; align-items: center; border-radius: 20px;">
                    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" style="width:1.4rem"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 19l-7-7 7-7m8 14l-7-7 7-7"></path></svg>
                </div>
                <span class="ml-3" style="color: #656565;">Back to Form</span>
            </div>
           <template v-if="currentComponent.value != 'ProbationStateReturner'">
                <template v-if="['objective_setting', 'probation_period'].includes(accessData.state)">
                    <div @click="$emit('change_component', 'MSetProbationObjective')" class="d-flex align-items-center" style="cursor: pointer;">
                        <div :style="{color: currentComponent.value == 'MSetProbationObjective'? style.activeColor : style.color, background: currentComponent.value=='MSetProbationObjective' ? style.activeBg : style.bg}"
                            class="font-weight-bold" style="width: 40px; height: 40px; display: flex; justify-content: center; align-items: center; border-radius: 20px;">
                                <span class="fa-fa-check" v-if="appraisalData.value.metaInfo.setting_general_objective_state"> <i class="fa fa-check"/> </span>
                                <span v-else="">1</span>
                            </div>
                        <span class="ml-3" :class="{'font-weight-bold': currentComponent.value=='MSetProbationObjective'}"
                            style="color: #656565;">Probation Period Objectives</span>
                    </div>
                </template>

                <template v-if="accessData.state == 'supervisor_assessment'">
                    
                    <div @click="$emit('change_component', 'SupervisorAssessment')" class="d-flex align-items-center" style="cursor: pointer;">
                        <div :style="{color: currentComponent.value == 'SupervisorAssessment'? style.activeColor : style.color, background: currentComponent.value=='SupervisorAssessment' ? style.activeBg : style.bg}"
                            class="font-weight-bold" style="width: 40px; height: 40px; display: flex; justify-content: center; align-items: center; border-radius: 20px;">
                            <span class="fa-fa-check" v-if="appraisalData.value.metaInfo.setting_overall_assessment_state"> <i class="fa fa-check"/> </span>
                            <span v-else="">1</span>
                        </div>
                        <span class="ml-3" :class="{'font-weight-bold': currentComponent.value=='SupervisorAssessment'}" style="color: #656565;">Overall Assessment</span>
                    </div>
                    <div style="margin-left:19px; width:2px; height:30px; background:#ebebeb" class="my-1"></div>

                    <div @click="$emit('change_component', 'ProbationPerformanceFeedback')" class="d-flex align-items-center" style="cursor: pointer;">
                        <div :style="{color: currentComponent.value == 'ProbationPerformanceFeedback'? style.activeColor : style.color, background: currentComponent.value=='ProbationPerformanceFeedback' ? style.activeBg : style.bg}"
                            class="font-weight-bold" style="width: 40px; height: 40px; display: flex; justify-content: center; align-items: center; border-radius: 20px;">
                            <span class="fa-fa-check" v-if="appraisalData.value.metaInfo.setting_performance_feedback_state"> <i class="fa fa-check"/> </span>
                            <span v-else="">2</span>
                        </div>
                        <span class="ml-3" :class="{'font-weight-bold': currentComponent.value=='ProbationPerformanceFeedback'}" style="color: #656565;">Performance Feedback</span>
                    </div>
                    <div style="margin-left:19px; width:2px; height:30px; background:#ebebeb" class="my-1"></div>

                    <div @click="$emit('change_component', 'ProbationWayForward')" class="d-flex align-items-center" style="cursor: pointer;">
                    <div :style="{color: currentComponent.value == 'ProbationWayForward'? style.activeColor : style.color, background: currentComponent.value=='ProbationWayForward' ? style.activeBg : style.bg}"
                        class="font-weight-bold" style="width: 40px; height: 40px; display: flex; justify-content: center; align-items: center; border-radius: 20px;">
                        <span class="fa-fa-check" v-if="appraisalData.value.metaInfo.setting_way_forward_state"> <i class="fa fa-check"/> </span>
                        <span v-else="">2</span>
                    </div>
                    <span class="ml-3" :class="{'font-weight-bold': currentComponent.value=='ProbationWayForward'}" style="color: #656565;">Way Forward</span>
                </div>
                </template>

                <template v-if="accessData.state == 'supervisor_assessment' || accessData.state == 'objective_setting'">
                    <div style="margin-left:19px; width:2px; height:30px; background:#ebebeb" class="my-1"></div>
                    <div @click="$emit('change_component', 'ProbationSubmitForm')"  class="d-flex align-items-center" style="cursor: pointer;">
                        <div :style="{color: currentComponent.value == 'ProbationSubmitForm'? style.activeColor : style.color, background: currentComponent.value=='ProbationSubmitForm' ? style.activeBg : style.bg}"
                            class="font-weight-bold"
                            style="width: 40px; height: 40px; display: flex; justify-content: center; align-items: center; border-radius: 20px;">
                            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" style="width:1.4rem"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 5l7 7-7 7M5 5l7 7-7 7"></path></svg>
                        </div>
                        <span class="ml-3" :class="{'font-weight-bold': currentComponent.value=='ProbationSubmitForm'}" style="color: #656565;">Validate and Submit</span>
                    </div>
                </template>
           </template>
        </template>
    `
}
