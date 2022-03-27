
SupervisorAssessment = {
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
            this.formData['has_sup_assessment'] = true
            this.formData['p2_q1'] = data.value['p2_q1']
            this.formData['p2_q2'] = data.value['p2_q2']
            this.formData['p2_q3'] = data.value['p2_q3']
            this.formData['p2_q4'] = data.value['p2_q4']
            this.formData['p2_q5'] = data.value['p2_q5']
        },
        async submitForm() {
            this.disableButton = true
            this.buttonText = "Saving..."
            result = await this.submitFunction(this.formData)
            if (result) {
                this.changeReadOnlyMode(changeData=false)
                if (this.appraisalData.value.metaInfo.setting_overall_assessment_state){
                    this.changeComponent('ProbationPerformanceFeedback')
                }
            }
            this.disableButton = false
            this.buttonText = "Save and next"
        }   
    },
    template: `
        <div>
            <h3 style="font-size: 20px;background: #ffffff;padding: 10px 0;margin-top: 20px;border-bottom: 4px solid #875a7b;text-transform: uppercase;">Overall Assessment</h3>
            <div class="py-3">
                <form class="form-group" @submit.prevent="submitForm">
                    <div class="form_buttons" v-if="appraisalData.value.metaInfo.hasCurrentComponentAccess">
                        <button type="button" class="btn btn-secondary text-white" @click="changeReadOnlyMode" v-if="!disableButton">{{ editButtonText }}</button>
                        <button  class="btn btn-secondary text-white" :disabled="disableButton" v-if="!readOnlyMode">{{ buttonText }}</button>
                    </div>
                    <div class="row my-2">
                        <div class="col-lg-6 border-grey border py-1 px-2" style="background:#875a7b; color:white;" >Employee Major Achievements</div>
                        <div class="col-lg-6 border-grey border py-1 px-2" style="background:#875a7b; color:white;" >Employee’s view on the job</div>
                        <div class="col-lg-6 border-grey border py-1 px-2 custom_font_size">{{ appraisalData.value.emp_major_achievements }}</div>
                        <div class="col-lg-6 border-grey border py-1 px-2 custom_font_size">{{ appraisalData.value.p3_emp_comments }}</div>
                    </div>
                    <label class="font-weight-normal mt-5" for="p2_q1"><strong>Quality and accuracy of work:</strong></label>
                    <select :disabled="readOnlyMode" class="form-control disabled-textarea mb-3" v-model="formData.p2_q1" name="p2_q1" id="p2_q1">
                        <option value="improvement_required">Improvement Required</option>
                        <option value="average">Average</option>
                        <option value="good">Good</option>
                        <option value="excellent">Excellent</option>
                    </select>
                    <label class="font-weight-normal" for="p2_q2"><strong>Efficiency:</strong></label>
                    <select :disabled="readOnlyMode" class="form-control disabled-textarea mb-3" v-model="formData.p2_q2" name="p2_q2" id="p2_q2">
                        <option value="improvement_required">Improvement Required</option>
                        <option value="average">Average</option>
                        <option value="good">Good</option>
                        <option value="excellent">Excellent</option>
                    </select>
                    <label class="font-weight-normal" for="p2_q3"><strong>Attendance and time keeping:</strong></label>
                    <select :disabled="readOnlyMode" class="form-control disabled-textarea mb-3" v-model="formData.p2_q3" name="p2_q3" id="p2_q3">
                        <option value="improvement_required">Improvement Required</option>
                        <option value="average">Average</option>
                        <option value="good">Good</option>
                        <option value="excellent">Excellent</option>
                    </select>
                    <label class="font-weight-normal" for="p2_q4"><strong>Understating and application of SCA policies and Values:</strong></label>
                    <select :disabled="readOnlyMode" class="form-control disabled-textarea mb-3" v-model="formData.p2_q4" name="p2_q4" id="p2_q4">
                        <option value="improvement_required">Improvement Required</option>
                        <option value="average">Average</option>
                        <option value="good">Good</option>
                        <option value="excellent">Excellent</option>
                    </select>
                    <label class="font-weight-normal" for="p2_q5"><strong>Work relationships (Teamwork, interpersonal and communication skills):</strong></label>
                    <select :disabled="readOnlyMode" class="form-control disabled-textarea mb-3" v-model="formData.p2_q5" name="p2_q5" id="p2_q5">
                        <option value="improvement_required">Improvement Required</option>
                        <option value="average">Average</option>
                        <option value="good">Good</option>
                        <option value="excellent">Excellent</option>
                    </select>
                </form>
            </div>    
        </div>
    `,
}