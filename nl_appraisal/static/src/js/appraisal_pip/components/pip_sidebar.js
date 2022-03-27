PipSideBarComponent = {
    props: {
        sideBarType: {
            default: 'employees'
        },
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
        <template v-if="sideBarType == 'managers'">
            <div v-if="currentComponent.value=='PIPAppraisalStateReturner'" @click="$emit('change_component', 'PIPFullForm')" class="d-flex align-items-center" style="cursor: pointer;">
                <div :style="{color: currentComponent.value == 'PIPAppraisalStateReturner'? style.activeColor : style.color, background: currentComponent.value=='PIPAppraisalStateReturner' ? style.activeBg : style.bg}"
                    class="font-weight-bold" style="width: 40px; height: 40px; display: flex; justify-content: center; align-items: center; border-radius: 20px;">
                    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" style="width:1.4rem"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 19l-7-7 7-7m8 14l-7-7 7-7"></path></svg>
                </div>
                <span class="ml-3" style="color: #656565;">Back to Form</span>
            </div>
            <template v-if="appraisalData.value.state == 'planning'">
                <div @click="$emit('change_component', 'MSetPipObjectives')" class="d-flex align-items-center" style="cursor: pointer;">
                    <div :style="{color: currentComponent.value == 'MSetPipObjectives'? style.activeColor : style.color, background: currentComponent.value=='MSetPipObjectives' ? style.activeBg : style.bg}"
                        class="font-weight-bold" style="width: 40px; height: 40px; display: flex; justify-content: center; align-items: center; border-radius: 20px;">
                        <span class="fa-fa-check" v-if="appraisalData.value.metaInfo.setting_pip_objective_state"> <i class="fa fa-check"/> </span>
                        <span v-else="">1</span>
                        </div>
                    <span :class="{'font-weight-bold': currentComponent.value=='MSetPipObjectives'}" class="ml-3"
                        style="color: #656565;">Set Objectives</span>
                </div>
                <div style="margin-left:19px; width:2px; height:30px; background:#ebebeb" class="my-1"></div>
                <div @click="$emit('change_component', 'MSetPipReviews')" class="d-flex align-items-center" style="cursor: pointer;">
                    <div :style="{color: currentComponent.value == 'MSetPipReviews'? style.activeColor : style.color, background: currentComponent.value=='MSetPipReviews' ? style.activeBg : style.bg}"
                        class="font-weight-bold" style="width: 40px; height: 40px; display: flex; justify-content: center; align-items: center; border-radius: 20px;">
                        <span class="fa-fa-check" v-if="appraisalData.value.metaInfo.setting_pip_review_state"> <i class="fa fa-check"/> </span>
                        <span v-else="">2</span>
                        </div>
                    <span :class="{'font-weight-bold': currentComponent.value=='MSetPipReviews'}" class="ml-3"
                        style="color: #656565;">Set Review Dates</span>
                </div>
            </template>
            <template v-if="appraisalData.value.state == 'assessment'">
                <div @click="$emit('change_component', 'MSetPipReviews')" class="d-flex align-items-center" style="cursor: pointer;">
                    <div :style="{color: currentComponent.value == 'MSetPipReviews'? style.activeColor : style.color, background: currentComponent.value=='MSetPipReviews' ? style.activeBg : style.bg}"
                        class="font-weight-bold" style="width: 40px; height: 40px; display: flex; justify-content: center; align-items: center; border-radius: 20px;">
                        <span class="fa-fa-check" v-if="appraisalData.value.metaInfo.setting_pip_review_assessment_state"> <i class="fa fa-check"/> </span>
                        <span v-else="">1</span>
                    </div>
                    <span :class="{'font-weight-bold': currentComponent.value=='MSetPipReviews'}" class="ml-3"
                        style="color: #656565;">Set Reviews</span>
                </div>
            </template>
            <template v-if="['planning', 'assessment'].includes(appraisalData.value.state)">
                <div style="margin-left:19px; width:2px; height:30px; background:#ebebeb" class="my-1"></div>
                <div @click="$emit('change_component', 'PIPSubmitForm')" class="d-flex align-items-center" style="cursor: pointer;">
                    <div :style="{color: currentComponent.value == 'PIPSubmitForm'? style.activeColor : style.color, background: currentComponent.value=='PIPSubmitForm' ? style.activeBg : style.bg}"
                        class="font-weight-bold"
                        style="width: 40px; height: 40px; display: flex; justify-content: center; align-items: center; border-radius: 20px;">
                        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" style="width:1.4rem"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 5l7 7-7 7M5 5l7 7-7 7"></path></svg>
                    </div>
                    <span :class="{'font-weight-bold': currentComponent.value=='PIPSubmitForm'}" class="ml-3" style="color: #656565;">Validate and Submit</span>
                </div>
            </template>
        </template>
        <template v-else="">
            <template v-if="appraisalData.value.state == 'final_comments'">
                <div @click="$emit('change_component', 'PIPFullForm')" class="d-flex align-items-center" style="cursor: pointer;">
                    <div :style="{color: currentComponent.value == 'PIPFullForm'? style.activeColor : style.color, background: currentComponent.value=='PIPFullForm' ? style.activeBg : style.bg}"
                        class="font-weight-bold" style="width: 40px; height: 40px; display: flex; justify-content: center; align-items: center; border-radius: 20px;">
                            <span class="fa-fa-check"> <i class="fa fa-check"/> </span>
                        </div>
                    <span :class="{'font-weight-bold': currentComponent.value=='PIPFullForm'}" class="ml-3"
                        style="color: #656565;">Full Form</span>
                </div>
            </template>
            <template v-if="['final_comments'].includes(appraisalData.value.state)">
                <div style="margin-left:19px; width:2px; height:30px; background:#ebebeb" class="my-1"></div>
                <div @click="$emit('change_component', 'PIPSubmitForm')" class="d-flex align-items-center" style="cursor: pointer;">
                    <div :style="{color: currentComponent.value == 'PIPSubmitForm'? style.activeColor : style.color, background: currentComponent.value=='PIPSubmitForm' ? style.activeBg : style.bg}"
                        class="font-weight-bold"
                        style="width: 40px; height: 40px; display: flex; justify-content: center; align-items: center; border-radius: 20px;">
                        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" style="width:1.4rem"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 5l7 7-7 7M5 5l7 7-7 7"></path></svg>
                    </div>
                    <span :class="{'font-weight-bold': currentComponent.value=='PIPSubmitForm'}" class="ml-3" style="color: #656565;">Sign and Submit</span>
                </div>
            </template>
        </template>
    `

    
}
