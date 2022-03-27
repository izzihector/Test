ProbationSelfAssessment = {
    inject: ['appraisalData', 'submitFunction', 'changeComponent', 'toggleChat'],
    data() {
        return {
            formData: {},
            disableButton: false,
            buttonText: "Save and next",
            readOnlyMode: true,
            editButtonText: "Edit"
        }
    },
    watch: {
        appraisalData: {
            handler(newVal, oldVal) {
                if (newVal.value) this.writeDataToForm(newVal)
            },
            immediate: true,
            deep: true
        },
    },
    methods: {
        changeReadOnlyMode(changeData=true) {
            this.readOnlyMode = !this.readOnlyMode
            if (this.readOnlyMode) {
                this.editButtonText = "Edit"
                this.toggleChat('block')
                if (changeData) this.writeDataToForm(this.appraisalData)
            }else {
                this.editButtonText = "Discard"
                this.toggleChat('none')
            }
        },
        writeDataToForm(data) {
            this.formData['appraisal_id'] = data.value['id']
            this.formData['setting_self_assessment_data'] = true
            this.formData['emp_major_achievements'] = data.value['emp_major_achievements']
            this.formData['p3_emp_comments'] = data.value['p3_emp_comments']
        },
        async submitForm() {
            this.disableButton = true
            this.buttonText = "Saving..."
            result = await this.submitFunction(this.formData)
            if (result) {
                this.changeReadOnlyMode(changeData=false)
                if (this.appraisalData.value.metaInfo.setting_self_assessment_state){
                    this.changeComponent('ProbationSubmitForm')
                }
            }
            this.disableButton = false
            this.buttonText = "Save and next"
        }
    },
    template: `
        <div>
            <h3 style="font-size: 20px;background: #ffffff;padding: 10px 0;margin-top: 20px;border-bottom: 4px solid #875a7b;text-transform: uppercase;">Employee Self Assessment</h3>
            <div class="py-3">
                <form class="form-group" @submit.prevent="submitForm">
                    <div class="form_buttons" v-if="appraisalData.value.metaInfo.hasCurrentComponentAccess">
                        <button type="button" class="btn btn-secondary text-white" @click="changeReadOnlyMode" v-if="!disableButton">{{ editButtonText }}</button>
                        <button  class="btn btn-secondary text-white" :disabled="disableButton" v-if="!readOnlyMode">{{ buttonText }}</button>
                    </div>
                    <div class="row my-5">
                        <div class="col-lg-6 border-grey border py-1 px-2" style="background:#875a7b; color:white;" >List of Objectives</div>
                        <div class="col-lg-6 border-grey border py-1 px-2" style="background:#875a7b; color:white;" >Expected Outcome</div>
                        <template v-for="obj in appraisalData.value.objectives">
                            <div class="col-lg-6 border-grey border py-1 px-2 custom_font_size">{{ obj.name }}</div>
                            <div class="col-lg-6 border-grey border py-1 px-2 custom_font_size">{{ obj.expected_outcome }}</div>
                        </template>
                    </div>
                    <label class="objective-title" for="emp_major_achievements">
                        Major Achievements:
                    </label>
                    <textarea class="form-control disabled-textarea" rows="5" placeholder="Employee Comment..." :disabled="readOnlyMode" 
                        v-model="formData.emp_major_achievements" name="emp_major_achievements" id="emp_major_achievements"></textarea>
                    <br/>
                    <label class="objective-title" for="p3_emp_comments">
                        Employee’s view on the job, work environment and working conditions
                    </label>
                    <textarea class="form-control disabled-textarea" rows="5" placeholder="Employee Comment..." :disabled="readOnlyMode" 
                    v-model="formData.p3_emp_comments" name="p3_emp_comments" id="p3_emp_comments"></textarea>
                    <br/>
            </form>
            </div>    
        </div>
    `,
}