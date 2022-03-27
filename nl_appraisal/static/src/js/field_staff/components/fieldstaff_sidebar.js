FieldSideBarComponent = {
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
            Welcome Employee 
        </template>
        <template v-if="sideBarType == 'managers'">
            <template v-if="['supervisor_review'].includes(accessData.state)">
                <div @click="$emit('change_component', 'FieldMPerformanceAssessment')" class="d-flex align-items-center" style="cursor: pointer;">
                    <div :style="{color: currentComponent.value == 'FieldMPerformanceAssessment'? style.activeColor : style.color, background: currentComponent.value=='FieldMPerformanceAssessment' ? style.activeBg : style.bg}"
                        class="font-weight-bold" style="width: 40px; height: 40px; display: flex; justify-content: center; align-items: center; border-radius: 20px;">
                            <span class="fa-fa-check" v-if="appraisalData.value.metaInfo.field_staff_performance_assessments_state"> <i class="fa fa-check"/> </span>
                            <span v-else="">1</span>
                        </div>
                    <span :class="{'font-weight-bold': currentComponent.value=='FieldMPerformanceAssessment'}" class="ml-3"
                        style="color: #656565;">Performance Assessmetent</span>
                </div>
                <div style="margin-left:19px; width:2px; height:30px; background:#ebebeb" class="my-1"></div>
                <div @click="$emit('change_component', 'FieldMEmployeeFeedback')" class="d-flex align-items-center" style="cursor: pointer;">
                    <div :style="{color: currentComponent.value == 'FieldMEmployeeFeedback'? style.activeColor : style.color, background: currentComponent.value=='FieldMEmployeeFeedback' ? style.activeBg : style.bg}"
                        class="font-weight-bold" style="width: 40px; height: 40px; display: flex; justify-content: center; align-items: center; border-radius: 20px;">
                            <span class="fa-fa-check" v-if="appraisalData.value.metaInfo.field_staff_employee_feedback_state"> <i class="fa fa-check"/> </span>
                            <span v-else="">2</span>
                        </div>
                    <span :class="{'font-weight-bold': currentComponent.value=='FieldMEmployeeFeedback'}" class="ml-3"
                        style="color: #656565;">Employee Feedback</span>
                </div>
                <div style="margin-left:19px; width:2px; height:30px; background:#ebebeb" class="my-1"></div>
                <div @click="$emit('change_component', 'FieldMPerformanceRating')" class="d-flex align-items-center" style="cursor: pointer;">
                    <div :style="{color: currentComponent.value == 'FieldMPerformanceRating'? style.activeColor : style.color, background: currentComponent.value=='FieldMPerformanceRating' ? style.activeBg : style.bg}"
                        class="font-weight-bold" style="width: 40px; height: 40px; display: flex; justify-content: center; align-items: center; border-radius: 20px;">
                            <span class="fa-fa-check" v-if="appraisalData.value.metaInfo.field_staff_overall_rating_state"> <i class="fa fa-check"/> </span>
                            <span v-else="">3</span>
                        </div>
                    <span :class="{'font-weight-bold': currentComponent.value=='FieldMPerformanceRating'}" class="ml-3"
                        style="color: #656565;">Overall Rating</span>
                </div>
                <div style="margin-left:19px; width:2px; height:30px; background:#ebebeb" class="my-1"></div>
                <div @click="$emit('change_component', 'FieldMOverAllAssessment')" class="d-flex align-items-center" style="cursor: pointer;">
                    <div :style="{color: currentComponent.value == 'FieldMOverAllAssessment'? style.activeColor : style.color, background: currentComponent.value=='FieldMOverAllAssessment' ? style.activeBg : style.bg}"
                        class="font-weight-bold" style="width: 40px; height: 40px; display: flex; justify-content: center; align-items: center; border-radius: 20px;">
                            <span class="fa-fa-check" v-if="appraisalData.value.metaInfo.field_staff_overall_assessment_state"> <i class="fa fa-check"/> </span>
                            <span v-else="">4</span>
                        </div>
                    <span :class="{'font-weight-bold': currentComponent.value=='FieldMOverAllAssessment'}" class="ml-3"
                        style="color: #656565;">Overall Assessment</span>
                </div>
            </template>
            <template v-if="accessData.state == 'supervisor_review'">
                <div style="margin-left:19px; width:2px; height:30px; background:#ebebeb" class="my-1"></div>
                <div @click="$emit('change_component', 'FieldSubmitForm')" class="d-flex align-items-center" style="cursor: pointer;">
                    <div :style="{color: currentComponent.value == 'FieldSubmitForm'? style.activeColor : style.color, background: currentComponent.value=='FieldSubmitForm' ? style.activeBg : style.bg}"
                        class="font-weight-bold"
                        style="width: 40px; height: 40px; display: flex; justify-content: center; align-items: center; border-radius: 20px;">
                        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" style="width:1.4rem"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 5l7 7-7 7M5 5l7 7-7 7"></path></svg>
                    </div>
                    <span :class="{'font-weight-bold': currentComponent.value=='FieldSubmitForm'}" class="ml-3" style="color: #656565;">Validate and Submit</span>
                </div>
            </template>
        </template>
    `
}
