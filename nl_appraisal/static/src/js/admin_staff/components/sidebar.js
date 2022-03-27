SideBarComponent = {
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
            <template v-if="['self_review'].includes(accessData.state)">
                <div @click="$emit('change_component', 'EObjectivesFeedback')" class="d-flex align-items-center" style="cursor: pointer;">
                    <div :style="{color: currentComponent.value == 'EObjectivesFeedback'? style.activeColor : style.color, background: currentComponent.value=='EObjectivesFeedback' ? style.activeBg : style.bg}"
                        class="font-weight-bold" style="width: 40px; height: 40px; display: flex; justify-content: center; align-items: center; border-radius: 20px;">
                        <span class="fa-fa-check" v-if="appraisalData.value.metaInfo.general_objective_feed_state"> <i class="fa fa-check"/> </span>
                                <span v-else="">1</span>
                    </div>
                    <span :class="{'font-weight-bold': currentComponent.value=='EObjectivesFeedback'}" class="ml-3"
                        style="color: #656565;">General Objectives</span>
                </div>
                <div style="margin-left:19px; width:2px; height:30px; background:#ebebeb" class="my-1"></div>
                <div @click="$emit('change_component', 'ELearningObjectivesFeedback')" class="d-flex align-items-center" style="cursor: pointer;">
                    <div :style="{color: currentComponent.value == 'ELearningObjectivesFeedback'? style.activeColor : style.color, background: currentComponent.value=='ELearningObjectivesFeedback' ? style.activeBg : style.bg}"
                        class="font-weight-bold" style="width: 40px; height: 40px; display: flex; justify-content: center; align-items: center; border-radius: 20px;">
                        <span class="fa-fa-check" v-if="appraisalData.value.metaInfo.learning_objective_feed_state"> <i class="fa fa-check"/> </span>
                        <span v-else="">2</span>
                    </div>
                    <span :class="{'font-weight-bold': currentComponent.value=='ELearningObjectivesFeedback'}" class="ml-3"
                        style="color: #656565;">Learning Objectives</span>
                </div>
                <div style="margin-left:19px; width:2px; height:30px; background:#ebebeb" class="my-1"></div>
                <div @click="$emit('change_component', 'ESelfAssessment')" class="d-flex align-items-center" style="cursor: pointer;">
                    <div :style="{color: currentComponent.value == 'ESelfAssessment'? style.activeColor : style.color, background: currentComponent.value=='ESelfAssessment' ? style.activeBg : style.bg}"
                        class="font-weight-bold" style="width: 40px; height: 40px; display: flex; justify-content: center; align-items: center; border-radius: 20px;">
                        <span class="fa-fa-check" v-if="appraisalData.value.metaInfo.employee_assessment_state"> <i class="fa fa-check"/> </span>
                        <span v-else="">3</span>
                    </div>
                    <span :class="{'font-weight-bold': currentComponent.value=='ESelfAssessment'}" class="ml-3" style="color: #656565;">Employee Assessment</span>
                </div>
                <div style="margin-left:19px; width:2px; height:30px; background:#ebebeb" class="my-1"></div>
                <div @click="$emit('change_component', 'ECareerAspiration')" class="d-flex align-items-center" style="cursor: pointer;">
                    <div :style="{color: currentComponent.value == 'ECareerAspiration'? style.activeColor : style.color, background: currentComponent.value=='ECareerAspiration' ? style.activeBg : style.bg}"
                        class="font-weight-bold" style="width: 40px; height: 40px; display: flex; justify-content: center; align-items: center; border-radius: 20px;">
                        <span class="fa-fa-check" v-if="appraisalData.value.metaInfo.employee_career_aspiration_state"> <i class="fa fa-check"/> </span>
                        <span v-else="">4</span>
                    </div>
                    <span :class="{'font-weight-bold': currentComponent.value=='ECareerAspiration'}" class="ml-3" style="color: #656565;">Career Aspirations</span>
                </div>
                <div style="margin-left:19px; width:2px; height:30px; background:#ebebeb" class="my-1"></div>
                <div @click="$emit('change_component', 'EUpwardFeedback')" class="d-flex align-items-center" style="cursor: pointer;">
                    <div :style="{color: currentComponent.value == 'EUpwardFeedback'? style.activeColor : style.color, background: currentComponent.value=='EUpwardFeedback' ? style.activeBg : style.bg}"
                        class="font-weight-bold" style="width: 40px; height: 40px; display: flex; justify-content: center; align-items: center; border-radius: 20px;">
                        <span class="fa-fa-check" v-if="appraisalData.value.metaInfo.emp_upward_feedback_state"> <i class="fa fa-check"/> </span>
                        <span v-else="">5</span>
                    </div>
                    <span :class="{'font-weight-bold': currentComponent.value=='EUpwardFeedback'}" class="ml-3" style="color: #656565;">Upward feedback</span>
                </div>
            </template>
            <template v-if="accessData.state == 'self_review'">
                <div style="margin-left:19px; width:2px; height:30px; background:#ebebeb" class="my-1"></div>
                <div @click="$emit('change_component', 'SubmitForm')" class="d-flex align-items-center" style="cursor: pointer;">
                    <div :style="{color: currentComponent.value == 'SubmitForm'? style.activeColor : style.color, background: currentComponent.value=='SubmitForm' ? style.activeBg : style.bg}"
                        class="font-weight-bold" style="width: 40px; height: 40px; display: flex; justify-content: center; align-items: center; border-radius: 20px;">
                        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" style="width:1.4rem"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 5l7 7-7 7M5 5l7 7-7 7"></path></svg>
                    </div>
                    <span :class="{'font-weight-bold': currentComponent.value=='SubmitForm'}" class="ml-3" style="color: #656565;">Finalize and Submit</span>
                </div>
            </template>
        </template>
        <template v-if="sideBarType == 'managers'">
            <div v-if="['supervisor_review'].includes(accessData.state) && currentComponent.value != 'AppraisalStateReturner'" class="position-absolute text-center text-sm fixed-bottom mb-4">
                <small @click="$emit('change_component','AppraisalStateReturner')" class="btn btn-secondary btn-sm btn-odoo">Move back to Self Assessment</small>
            </div>
            <div v-if="currentComponent.value=='AppraisalStateReturner'" @click="$emit('change_component', accessData.state=='final_comments' ? 'FullForm': accessData.state == '2nd_supervisor_review' ? 'SecondSupervisor' : 'MObjectiveFeedback')"  class="d-flex align-items-center" style="cursor: pointer;">
                <div style="color: #999; background: #ebebeb; width: 40px; height: 40px; display: flex; justify-content: center; align-items: center; border-radius: 20px;" class="font-weight-bold">
                    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" style="width:1.4rem"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 19l-7-7 7-7m8 14l-7-7 7-7"></path></svg>
                </div>
                <span class="ml-3" style="color: #656565;">Back to Form</span>
            </div>
            <template v-if="currentComponent.value != 'AppraisalStateReturner'">
                <template v-if="['objective_setting', 'performance_period'].includes(accessData.state)">
                    <div @click="$emit('change_component', 'MSetObjective')" class="d-flex align-items-center" style="cursor: pointer;">
                        <div :style="{color: currentComponent.value == 'MSetObjective'? style.activeColor : style.color, background: currentComponent.value=='MSetObjective' ? style.activeBg : style.bg}"
                            class="font-weight-bold" style="width: 40px; height: 40px; display: flex; justify-content: center; align-items: center; border-radius: 20px;">
                                <span class="fa-fa-check" v-if="appraisalData.value.metaInfo.setting_general_objective_state"> <i class="fa fa-check"/> </span>
                                <span v-else="">1</span>
                            </div>
                        <span :class="{'font-weight-bold': currentComponent.value=='MSetObjective'}" class="ml-3"
                            style="color: #656565;">General Objectives</span>
                    </div>
                    <div style="margin-left:19px; width:2px; height:30px; background:#ebebeb" class="my-1"></div>
                    <div @click="$emit('change_component', 'MSetLearningObjective')" class="d-flex align-items-center" style="cursor: pointer;">
                        <div :style="{color: currentComponent.value == 'MSetLearningObjective'? style.activeColor : style.color, background: currentComponent.value=='MSetLearningObjective' ? style.activeBg : style.bg}"
                            class="font-weight-bold" style="width: 40px; height: 40px; display: flex; justify-content: center; align-items: center; border-radius: 20px;">
                                <span class="fa-fa-check" v-if="appraisalData.value.metaInfo.setting_learning_objective_state"> <i class="fa fa-check"/> </span>
                                <span v-else="">2</span>
                            </div>
                        <span :class="{'font-weight-bold': currentComponent.value=='MSetLearningObjective'}" class="ml-3"
                            style="color: #656565;">Learning Objectives</span>
                    </div>
                </template>
                <template v-if="accessData.state == 'supervisor_review'">
                    <div @click="$emit('change_component', 'MObjectiveFeedback')" class="d-flex align-items-center" style="cursor: pointer;">
                        <div :style="{color: currentComponent.value == 'MObjectiveFeedback'? style.activeColor : style.color, background: currentComponent.value=='MObjectiveFeedback' ? style.activeBg : style.bg}"
                            class="font-weight-bold" style="width: 40px; height: 40px; display: flex; justify-content: center; align-items: center; border-radius: 20px;">
                            <span class="fa-fa-check" v-if="appraisalData.value.metaInfo.setting_learning_objective_state"> <i class="fa fa-check"/> </span>
                            <span v-else="">1</span>
                        </div>
                        <span :class="{'font-weight-bold': currentComponent.value=='MObjectiveFeedback'}" class="ml-3" style="color: #656565;">General Objectives</span>
                    </div>
                    <div style="margin-left:19px; width:2px; height:30px; background:#ebebeb" class="my-1"></div>
                    <div @click="$emit('change_component', 'MObjectiveLearningFeedback')" class="d-flex align-items-center" style="cursor: pointer;">
                        <div :style="{color: currentComponent.value == 'MObjectiveLearningFeedback'? style.activeColor : style.color, background: currentComponent.value=='MObjectiveLearningFeedback' ? style.activeBg : style.bg}"
                            class="font-weight-bold" style="width: 40px; height: 40px; display: flex; justify-content: center; align-items: center; border-radius: 20px;">
                            <span class="fa-fa-check" v-if="appraisalData.value.metaInfo.learning_objective_feed_state"> <i class="fa fa-check"/> </span>
                            <span v-else="">2</span>
                        </div>
                        <span :class="{'font-weight-bold': currentComponent.value=='MObjectiveLearningFeedback'}" class="ml-3" style="color: #656565;">Learning Objectives</span>
                    </div>
                    <div style="margin-left:19px; width:2px; height:30px; background:#ebebeb" class="my-1"></div>
                    <div @click="$emit('change_component', 'MEmployeeAssessment')" class="d-flex align-items-center" style="cursor: pointer;">
                        <div :style="{color: currentComponent.value == 'MEmployeeAssessment'? style.activeColor : style.color, background: currentComponent.value=='MEmployeeAssessment' ? style.activeBg : style.bg}"
                            class="font-weight-bold" style="width: 40px; height: 40px; display: flex; justify-content: center; align-items: center; border-radius: 20px;">
                            <span class="fa-fa-check" v-if="appraisalData.value.metaInfo.employee_assessment_state"> <i class="fa fa-check"/> </span>
                            <span v-else="">3</span>
                        </div>
                        <span :class="{'font-weight-bold': currentComponent.value=='MEmployeeAssessment'}" class="ml-3" style="color: #656565;">Employee Assessment</span>
                    </div>
                    <div style="margin-left:19px; width:2px; height:30px; background:#ebebeb" class="my-1"></div>
                    <div @click="$emit('change_component', 'MCareerAspiration')" class="d-flex align-items-center" style="cursor: pointer;">
                        <div :style="{color: currentComponent.value == 'MCareerAspiration'? style.activeColor : style.color, background: currentComponent.value=='MCareerAspiration' ? style.activeBg : style.bg}"
                            class="font-weight-bold" style="width: 40px; height: 40px; display: flex; justify-content: center; align-items: center; border-radius: 20px;">
                            <span class="fa-fa-check" v-if="appraisalData.value.metaInfo.employee_career_aspiration_state"> <i class="fa fa-check"/> </span>
                            <span v-else="">4</span>
                        </div>
                        <span :class="{'font-weight-bold': currentComponent.value=='MCareerAspiration'}" class="ml-3" style="color: #656565;">Career Aspirations</span>
                    </div>
                    <div style="margin-left:19px; width:2px; height:30px; background:#ebebeb" class="my-1"></div>
                    <div @click="$emit('change_component', 'MSetObjectiveNextYear')" class="d-flex align-items-center" style="cursor: pointer;">
                        <div :style="{color: currentComponent.value == 'MSetObjectiveNextYear'? style.activeColor : style.color, background: currentComponent.value=='MSetObjectiveNextYear' ? style.activeBg : style.bg}"
                            class="font-weight-bold" style="width: 40px; height: 40px; display: flex; justify-content: center; align-items: center; border-radius: 20px;">
                            <span class="fa-fa-check" v-if="appraisalData.value.metaInfo.setting_general_objective_state_next"> <i class="fa fa-check"/> </span>
                            <span v-else="">5</span>
                        </div>
                        <span :class="{'font-weight-bold': currentComponent.value=='MSetObjectiveNextYear'}" class="ml-3" style="color: #656565;">Next Year General Objectives</span>
                    </div>
                    <div style="margin-left:19px; width:2px; height:30px; background:#ebebeb" class="my-1"></div>
                    <div @click="$emit('change_component', 'MSetLearningObjectiveNextYear')" class="d-flex align-items-center" style="cursor: pointer;">
                        <div :style="{color: currentComponent.value == 'MSetLearningObjectiveNextYear'? style.activeColor : style.color, background: currentComponent.value=='MSetLearningObjectiveNextYear' ? style.activeBg : style.bg}"
                            class="font-weight-bold" style="width: 40px; height: 40px; display: flex; justify-content: center; align-items: center; border-radius: 20px;">
                            <span class="fa-fa-check" v-if="appraisalData.value.metaInfo.setting_learning_objective_state_next"> <i class="fa fa-check"/> </span>
                            <span v-else="">6</span>
                        </div>
                        <span :class="{'font-weight-bold': currentComponent.value=='MSetLearningObjectiveNextYear'}" class="ml-3" style="color: #656565;">Next Year Learning Objectives</span>
                    </div>
                    <div style="margin-left:19px; width:2px; height:30px; background:#ebebeb" class="my-1"></div>
                    <div @click="$emit('change_component', 'MPerformanceRating')" class="d-flex align-items-center" style="cursor: pointer;">
                        <div :style="{color: currentComponent.value == 'MPerformanceRating'? style.activeColor : style.color, background: currentComponent.value=='MPerformanceRating' ? style.activeBg : style.bg}"
                            class="font-weight-bold" style="width: 40px; height: 40px; display: flex; justify-content: center; align-items: center; border-radius: 20px;">
                            <span class="fa-fa-check" v-if="appraisalData.value.metaInfo.setting_performance_rating_state"> <i class="fa fa-check"/> </span>
                            <span v-else="">7</span>
                        </div>
                        <span :class="{'font-weight-bold': currentComponent.value=='MPerformanceRating'}" class="ml-3" style="color: #656565;">Performance Rating</span>
                    </div>
                </template>
                <template v-if="accessData.state == 'supervisor_review' || accessData.state == 'objective_setting'">
                    <div style="margin-left:19px; width:2px; height:30px; background:#ebebeb" class="my-1"></div>
                    <div @click="$emit('change_component', 'SubmitForm')" class="d-flex align-items-center mb-5" style="cursor: pointer;">
                        <div :style="{color: currentComponent.value == 'SubmitForm'? style.activeColor : style.color, background: currentComponent.value=='SubmitForm' ? style.activeBg : style.bg}"
                            class="font-weight-bold"
                            style="width: 40px; height: 40px; display: flex; justify-content: center; align-items: center; border-radius: 20px;">
                            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" style="width:1.4rem"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 5l7 7-7 7M5 5l7 7-7 7"></path></svg>
                        </div>
                        <span :class="{'font-weight-bold': currentComponent.value=='SubmitForm'}" class="ml-3" style="color: #656565;">Validate and Submit</span>
                    </div>
                </template>
            </template>
        </template>
    `
}
