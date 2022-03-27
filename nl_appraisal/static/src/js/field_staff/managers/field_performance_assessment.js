FieldMPerformanceAssessment = {
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
    computed: {
        totalScore() {
            var avgScore = (this.formData['field_p1_rating1'] + this.formData['field_p1_rating2'] + this.formData['field_p1_rating3'] + this.formData['field_p1_rating4']
                + this.formData['field_p1_rating5'] + this.formData['field_p1_rating6'] + this.formData['field_p1_rating7'] + this.formData['field_p1_rating8']
                + this.formData['field_p1_rating9'] + this.formData['field_p1_rating10']) / 10
            if (!avgScore) {
                avgScore = 0
            } 
        
            this.formData['field_p1_total_score'] = avgScore
            return avgScore
        }
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
            this.formData['has_sup_fieldstaff_performance_assessments'] = true
            this.formData['field_p1_rating1'] = data.value['field_p1_rating1'] || ""
            this.formData['field_p1_rating2'] = data.value['field_p1_rating2'] || ""
            this.formData['field_p1_rating3'] = data.value['field_p1_rating3'] || ""
            this.formData['field_p1_rating4'] = data.value['field_p1_rating4'] || ""
            this.formData['field_p1_rating5'] = data.value['field_p1_rating5'] || ""
            this.formData['field_p1_rating6'] = data.value['field_p1_rating6'] || ""
            this.formData['field_p1_rating7'] = data.value['field_p1_rating7'] || ""
            this.formData['field_p1_rating8'] = data.value['field_p1_rating8'] || ""
            this.formData['field_p1_rating9'] = data.value['field_p1_rating9'] || ""
            this.formData['field_p1_rating10'] = data.value['field_p1_rating10'] || ""
            this.formData['field_p1_total_score'] = data.value['field_p1_total_score']
        },
        async submitForm() {
            this.disableButton = true
            this.buttonText = "Saving..."
            result = await this.submitFunction(this.formData)
            if (result) {
                this.changeReadOnlyMode(changeData=false)
                if (this.appraisalData.value.metaInfo.field_staff_performance_assessments_state){
                    this.changeComponent('FieldMEmployeeFeedback')
                }
            }
            this.disableButton = false
            this.buttonText = "Save and next"
        }
    },
    template: `
        <div>
            <h4 style="font-size: 20px;background: #ffffff;padding: 10px 0;margin-top: 20px;border-bottom: 4px solid #875a7b;text-transform: uppercase;">
                Performance assessment by supervisor in discussion with employee
            </h4>
            <div class="text-center">
                <svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" data-name="Layer 1" width="250" height="250" viewBox="0 0 793.56289 662.46368"><rect x="167.35474" y="277.15781" width="630.1657" height="31.98284" transform="translate(-285.26597 168.12179) rotate(-30.64932)" fill="#f2f2f2"></rect><rect x="285.18618" y="304.09069" width="630.16572" height="31.98284" transform="translate(-282.53524 231.95258) rotate(-30.64932)" fill="#f2f2f2"></rect><rect x="389.55116" y="333.54852" width="630.16572" height="31.98284" transform="translate(-282.9729 289.27113) rotate(-30.64932)" fill="#f2f2f2"></rect><circle cx="353.12035" cy="206.84364" r="169.73576" fill="#fff"></circle><path d="M385.34074,325.61183c0-94.28862,76.70937-170.99819,170.99819-170.99819s170.99819,76.70957,170.99819,170.99819S650.62775,496.61,556.33893,496.61,385.34074,419.90044,385.34074,325.61183Zm2.525,0c0,92.89626,75.57675,168.47321,168.47322,168.47321s168.47322-75.577,168.47322-168.47321S649.2354,157.13861,556.33893,157.13861,387.86571,232.71556,387.86571,325.61183Z" transform="translate(-203.21856 -118.76816)" fill="#3f3d56"></path><path d="M526.08167,326.34979v0A30.25726,30.25726,0,1,1,556.3389,356.607,30.25726,30.25726,0,0,1,526.08167,326.34976Zm30.25723-28.7813a28.81369,28.81369,0,0,0-28.7813,28.78132v0a28.7813,28.7813,0,1,0,28.7813-28.78132Z" transform="translate(-203.21856 -118.76816)" fill="#3f3d56" style="isolation:isolate"></path><path d="M498.77636,326.34979v0a57.56256,57.56256,0,1,1,57.56254,57.56259A57.56254,57.56254,0,0,1,498.77636,326.34976Zm57.56254-56.08661a56.08661,56.08661,0,1,0,56.08661,56.08663,56.14995,56.14995,0,0,0-56.08661-56.08663Z" transform="translate(-203.21856 -118.76816)" fill="#ccc" style="isolation:isolate"></path><path d="M444.16568,326.34976A112.17322,112.17322,0,1,1,556.3389,438.523,112.30013,112.30013,0,0,1,444.16568,326.34976ZM556.3389,215.65255A110.69725,110.69725,0,1,0,667.03618,326.34981,110.82276,110.82276,0,0,0,556.3389,215.65255Z" transform="translate(-203.21856 -118.76816)" fill="#ccc" style="isolation:isolate"></path><circle cx="353.12035" cy="206.84365" r="14.02164" fill="#875a7b" style="isolation:isolate"></circle><circle cx="316.95924" cy="247.43264" r="14.02164" fill="#875a7b" style="isolation:isolate"></circle><circle cx="458.0353" cy="241.52879" r="14.02164" fill="#875a7b" style="isolation:isolate"></circle><circle cx="353.12035" cy="206.84365" r="6.64182" fill="#2f2e41"></circle><circle cx="458.0353" cy="241.52879" r="6.64184" fill="#2f2e41"></circle><circle cx="316.95924" cy="248.17061" r="6.64183" fill="#2f2e41"></circle><circle cx="43.16807" cy="132.3075" r="6.64182" fill="#875a7b"></circle><polygon points="352.751 132.677 61.248 132.677 61.248 131.201 354.228 131.201 354.228 207.212 352.751 207.212 352.751 132.677" fill="#2f2e41"></polygon><path d="M227.199,251.07566a19.18754,19.18754,0,1,1,19.18756,19.18752A19.18751,19.18751,0,0,1,227.199,251.07566Zm19.18756-17.71155a17.71156,17.71156,0,1,0,17.71153,17.71155,17.73186,17.73186,0,0,0-17.71153-17.71155Z" transform="translate(-203.21856 -118.76816)" fill="#2f2e41"></path><circle cx="87.44698" cy="323.44473" r="6.64183" fill="#875a7b"></circle><path d="M271.478,442.21288h0a19.18751,19.18751,0,1,1,19.18751,19.18751A19.18753,19.18753,0,0,1,271.478,442.21288Zm19.18751-17.71156a17.71155,17.71155,0,1,0,17.71153,17.71156,17.73188,17.73188,0,0,0-17.71153-17.71156Z" transform="translate(-203.21856 -118.76816)" fill="#2f2e41"></path><circle cx="663.93217" cy="163.30273" r="6.64183" fill="#875a7b"></circle><path d="M847.96319,282.07088a19.18753,19.18753,0,1,1,19.18754,19.18754A19.18751,19.18751,0,0,1,847.96319,282.07088Zm19.18754-17.7115a17.73182,17.73182,0,0,0-17.71155,17.7115v0a17.71157,17.71157,0,1,0,17.71155-17.71158Z" transform="translate(-203.21856 -118.76816)" fill="#2f2e41"></path><polygon points="457.297 165.528 645.471 162.565 645.494 164.04 458.773 166.981 458.773 241.529 457.297 241.529 457.297 165.528" fill="#2f2e41"></polygon><polygon points="105.897 322.707 316.221 322.707 316.221 248.171 317.697 248.171 317.697 324.182 105.897 324.182 105.897 322.707" fill="#2f2e41"></polygon><rect x="2.57907" y="166.99264" width="81.178" height="5.16587" fill="#ccc"></rect><rect x="2.57907" y="181.75227" width="81.178" height="5.16587" fill="#ccc"></rect><rect x="2.57907" y="196.51191" width="81.178" height="5.16587" fill="#ccc"></rect><rect x="46.85793" y="358.12988" width="81.178" height="5.16586" fill="#ccc"></rect><rect x="46.85793" y="372.8895" width="81.178" height="5.16586" fill="#ccc"></rect><rect x="46.85793" y="387.64914" width="81.178" height="5.16586" fill="#ccc"></rect><rect x="623.34318" y="198.72585" width="81.17797" height="5.16587" fill="#ccc"></rect><rect x="623.34318" y="213.48548" width="81.17797" height="5.16587" fill="#ccc"></rect><rect x="623.34318" y="228.24511" width="81.17797" height="5.16586" fill="#ccc"></rect><polygon points="743.166 638.861 731.622 642.987 710.214 600.421 727.253 594.332 743.166 638.861" fill="#ffb8b8"></polygon><path d="M916.10405,781.07119l-.16846-.4707a15.40481,15.40481,0,0,1,9.31128-19.66748l22.73559-8.12549,5.34668,14.96045Z" transform="translate(-203.21856 -118.76816)" fill="#2f2e41"></path><polygon points="668.095 650.28 655.835 650.279 650.003 602.991 668.097 602.992 668.095 650.28" fill="#ffb8b8"></polygon><path d="M874.43974,780.932l-39.53076-.00146v-.5a15.38646,15.38646,0,0,1,15.38672-15.38623h.001l24.1438.001Z" transform="translate(-203.21856 -118.76816)" fill="#2f2e41"></path><path d="M899.2535,466.93834l-5.33176-10.53543s-19.86256,4.97638-21.66824,16.48819Z" transform="translate(-203.21856 -118.76816)" fill="#875a7b"></path><polygon points="718.035 468.635 703.535 549.548 742.035 617.635 719.035 626.635 680.035 560.635 675.035 542.635 672.035 636.635 651.292 636.005 641.781 548.232 657.035 466.635 718.035 468.635" fill="#2f2e41"></polygon><path d="M852,602c-.44995-2.00391-1.74065-63.17326-1.74065-63.17326s21.32544-70.00879,21.52051-70.584l.07617-.22461,16.19068-6.07032c.22705-.10351,5.62134-2.50683,10.03564-.5039a8.65063,8.65063,0,0,1,4.60083,5.65429c1.83643,1.36817,15.07032,16.19239,15.07032,36.29981l.49951,47.44922,11.095,51.44043-.49048.10449c-.303.06445-13.82739,4.13867-35.12842,4.13867C881.89363,606.53084,852,602,852,602Z" transform="translate(-203.21856 -118.76816)" fill="#3f3d56"></path><circle cx="674.14281" cy="312.43466" r="21.88287" fill="#ffb8b8"></circle><polygon points="705.318 408.841 667.035 462.257 661.381 437.312 705.318 408.841" opacity="0.2"></polygon><path d="M840.58961,582.17691a9.39072,9.39072,0,0,0,8.79948-11.39812l28.44617-17.44924L862.1276,545.981l-24.60481,17.69671a9.44164,9.44164,0,0,0,3.06682,18.49919Z" transform="translate(-203.21856 -118.76816)" fill="#ffb8b8"></path><polygon points="657.035 427.635 647.292 434.462 655.555 449.135 667.035 439.635 657.035 427.635" fill="#875a7b"></polygon><path d="M855.15291,546.83358l22.917-26.56348-8.78027-36.63867a16.031,16.031,0,0,1,29.70483-11.33594l.19947.37109,8.09057,54.40821-40.6543,41.67089Z" transform="translate(-203.21856 -118.76816)" fill="#3f3d56"></path><path d="M896.00075,450.20218l-18.16292.65194c-1.10712.03974-4.11189-11.90855-4.50522-14.38721a6.76485,6.76485,0,0,0-7.05681-5.47254c-1.35961.12843-4.78806-2.41166-8.32588-5.4194-6.71659-5.71022-6.36717-16.43488,1.011-21.26q.30247-.19782.59374-.36125c4.65454-2.6052,10.09951-3.48006,15.43312-3.54678,4.83507-.06047,9.8072.54809,14.0668,2.83662,7.63654,4.10284,11.70069,13.06869,12.05768,21.73025s-2.41975,17.131-5.57072,25.207" transform="translate(-203.21856 -118.76816)" fill="#2f2e41"></path><path d="M995.78144,781.23184h-221a1,1,0,0,1,0-2h221a1,1,0,0,1,0,2Z" transform="translate(-203.21856 -118.76816)" fill="#3f3d56"></path></svg>
            </div>
            <p class="page-hint">
                Average of the above ratings (can be weighted in the judgement of the evaluator based on performance throughout the review period.).
                <strong> 
                    4.5 – 5 Exceptional/outstanding, 
                    3.5 – 4.4 Exceeds Expected Performance 2.5 – 3.4,          
                    Meets Expected Performance, 1.5 – 2.4          
                    Required performance improvement, 1 – 1.4             
                    Unsatisfactory/Unacceptable performance,
                </strong>
            </p>
            
            <div class="py-3">
                <form class="form-group" @submit.prevent="submitForm">
                    <div class="form_buttons" v-if="appraisalData.value.metaInfo.hasCurrentComponentAccess">
                        <button type="button" class="btn btn-secondary text-white" @click="changeReadOnlyMode" v-if="!disableButton">{{ editButtonText }}</button>
                        <button  class="btn btn-secondary text-white" :disabled="disableButton" v-if="!readOnlyMode">{{ buttonText }}</button>
                    </div>
                    <div class="row bg-white font-wieght-bold text-center">
                        <div class="col-lg-3 border-grey headr border py-1 px-2" >
                            <strong>Evaluation Area</strong>
                        </div>
                        <div class="col-lg-7 border-grey headr border py-1 px-2" >
                            <strong>Description/ Assessment Question</strong>
                        </div>
                        <div class="col-lg-2 border-grey headr border py-1 px-2" >
                            <strong>Ratings</strong>
                        </div>
                    </div>
                    <div class="row" style="font-size: 15px">
                        <div class="p-0">
                            <div class="row bg-white">
                                <div class="col-lg-3 border-grey border py-1 px-2 odoo-cell-grey d-flex align-items-center">1. Work Performance</div>
                                <div class="col-lg-7 border-grey border py-1 px-2 odoo-cell-grey">How is the employee performing his/her routine-tasks based on job description?</div>
                                <div class="col-lg-2 odoo-cell-grey" style="padding: 0px">
                                    <select class="form-control full_height_input small_text" placeholder="Ratings" :disabled="readOnlyMode" v-model="formData.field_p1_rating1" name="field_p1_rating1" id="field_p1_rating1">
                                        <option value='' selected=""><span class="text-muted">Ratings...</span></option>
                                        <option v-for="number in 5" :value="number">{{ number }}</option>
                                    </select>
                                </div>
                            </div>
                            <div class="row bg-white">
                                <div class="col-lg-3 border-grey border py-1 px-2 odoo-cell-grey d-flex align-items-center">2. Discipline</div>
                                <div class="col-lg-7 border-grey border py-1 px-2 odoo-cell-grey">How disciplined or obedient is the employee?</div>
                                <div class="col-lg-2 odoo-cell-grey" style="padding: 0px">
                                    <select class="form-control full_height_input small_text" placeholder="Ratings" :disabled="readOnlyMode" v-model="formData.field_p1_rating2" name="field_p1_rating2" id="field_p1_rating2">
                                        <option value='' selected=""><span class="text-muted">Ratings...</span></option>
                                        <option v-for="number in 5" :value="number">{{ number }}</option>
                                    </select>
                                </div>
                            </div>
                            <div class="row bg-white">
                                <div class="col-lg-3 border-grey border py-1 px-2 odoo-cell-grey d-flex align-items-center">3. Behaviour</div>
                                <div class="col-lg-7 border-grey border py-1 px-2 odoo-cell-grey">How is the overall behaviour and conduct of the employee, how does he/she behave with his/her other colleagues</div>
                                <div class="col-lg-2 odoo-cell-grey" style="padding: 0px">
                                    <select class="form-control full_height_input small_text" placeholder="Ratings" :disabled="readOnlyMode" v-model="formData.field_p1_rating3" name="field_p1_rating3" id="field_p1_rating3">
                                        <option value='' selected=""><span class="text-muted">Ratings...</span></option>
                                        <option v-for="number in 5" :value="number">{{ number }}</option>
                                    </select>
                                </div>
                            </div>
                            <div class="row bg-white">
                                <div class="col-lg-3 border-grey border py-1 px-2 odoo-cell-grey d-flex align-items-center">4. Punctuality</div>
                                <div class="col-lg-7 border-grey border py-1 px-2 odoo-cell-grey">
                                    How is the attendance and visibility of the employee during the official office hours?
                                </div>
                                <div class="col-lg-2 odoo-cell-grey" style="padding: 0px">
                                    <select class="form-control full_height_input small_text" placeholder="Ratings" :disabled="readOnlyMode" v-model="formData.field_p1_rating4" name="field_p1_rating4" id="field_p1_rating4">
                                        <option value='' selected=""><span class="text-muted">Ratings...</span></option>
                                        <option v-for="number in 5" :value="number">{{ number }}</option>
                                    </select>
                                </div>
                            </div>
                            <div class="row bg-white">
                                <div class="col-lg-3 border-grey border py-1 px-2 odoo-cell-grey d-flex align-items-center">5. Response to Instructions</div>
                                <div class="col-lg-7 border-grey border py-1 px-2 odoo-cell-grey">
                                    How does the employee take the formal instruction that you give to them as the supervisor? 
                                    How quickly does the employee respond to the instructions, do they ignore instructions or delay in 
                                    implementing the instructions?
                                </div>
                                <div class="col-lg-2 odoo-cell-grey" style="padding: 0px">
                                    <select class="form-control full_height_input small_text" placeholder="Ratings" :disabled="readOnlyMode" v-model="formData.field_p1_rating5" name="field_p1_rating5" id="field_p1_rating5">
                                        <option value='' selected=""><span class="text-muted">Ratings...</span></option>
                                        <option v-for="number in 5" :value="number">{{ number }}</option>
                                    </select>
                                </div>
                            </div>
                            <div class="row bg-white">
                                <div class="col-lg-3 border-grey border py-1 px-2 odoo-cell-grey d-flex align-items-center">6. Helpfulness & Initiative</div>
                                <div class="col-lg-7 border-grey border py-1 px-2 odoo-cell-grey">
                                    <strong>Does the employee</strong> show willingness to help others without being asked, suggests ideas, contributes to team building and volunteers when needed?
                                </div>
                                <div class="col-lg-2 odoo-cell-grey" style="padding: 0px">
                                    <select class="form-control full_height_input small_text" placeholder="Ratings" :disabled="readOnlyMode" v-model="formData.field_p1_rating6" name="field_p1_rating6" id="field_p1_rating6">
                                        <option value='' selected=""><span class="text-muted">Ratings...</span></option>
                                        <option v-for="number in 5" :value="number">{{ number }}</option>
                                    </select>
                                </div>
                            </div>
                            <div class="row bg-white">
                                <div class="col-lg-3 border-grey border py-1 px-2 odoo-cell-grey d-flex align-items-center">7. Respect SCA policies and Values</div>
                                <div class="col-lg-7 border-grey border py-1 px-2 odoo-cell-grey">
                                    Does your employee respect all the contents of SCA policies and values? Does the employee consider the policies and 
                                    values before he/she decides to do something?
                                    <br/>
                                    <strong>SCA values: Responsiveness, Equality, Impartiality, Social Justice, and Integrity</strong>
                                </div>
                                <div class="col-lg-2 odoo-cell-grey" style="padding: 0px">
                                    <select class="form-control full_height_input small_text" placeholder="Ratings" :disabled="readOnlyMode" v-model="formData.field_p1_rating7" name="field_p1_rating7" id="field_p1_rating7">
                                        <option value='' selected=""><span class="text-muted">Ratings...</span></option>
                                        <option v-for="number in 5" :value="number">{{ number }}</option>
                                    </select>
                                </div>
                            </div>
                            <div class="row bg-white">
                                <div class="col-lg-3 border-grey border py-1 px-2 odoo-cell-grey d-flex align-items-center">8. Quality of Work</div>
                                <div class="col-lg-7 border-grey border py-1 px-2 odoo-cell-grey">
                                    Does the employee complete work/tasks to a high-level standard, pays attention to neatness and safety instructions?
                                </div>
                                <div class="col-lg-2 odoo-cell-grey" style="padding: 0px">
                                    <select class="form-control full_height_input small_text" placeholder="Ratings" :disabled="readOnlyMode" v-model="formData.field_p1_rating8" name="field_p1_rating8" id="field_p1_rating8">
                                        <option value='' selected=""><span class="text-muted">Ratings...</span></option>
                                        <option v-for="number in 5" :value="number">{{ number }}</option>
                                    </select>
                                </div>
                            </div>
                            <div class="row bg-white">
                                <div class="col-lg-3 border-grey border py-1 px-2 odoo-cell-grey d-flex align-items-center">9. Supervision</div>
                                <div class="col-lg-7 border-grey border py-1 px-2 odoo-cell-grey">
                                    Does the employee work independently with minimum supervision?  Does the employee remain calm and focused under pressure?
                                </div>
                                <div class="col-lg-2 odoo-cell-grey" style="padding: 0px">
                                    <select class="form-control full_height_input small_text" placeholder="Ratings" :disabled="readOnlyMode" v-model="formData.field_p1_rating9" name="field_p1_rating9" id="field_p1_rating9">
                                        <option value='' selected=""><span class="text-muted">Ratings...</span></option>
                                        <option v-for="number in 5" :value="number">{{ number }}</option>
                                    </select>
                                </div>
                            </div>
                            <div class="row bg-white">
                                <div class="col-lg-3 border-grey border py-1 px-2 odoo-cell-grey d-flex align-items-center">10. Efficiency</div>
                                <div class="col-lg-7 border-grey border py-1 px-2 odoo-cell-grey">
                                    Does the employee appropriately use/utilize SCA assets, equipment and supplies given to him/her?
                                </div>
                                <div class="col-lg-2 odoo-cell-grey" style="padding: 0px">
                                    <select class="form-control full_height_input small_text" placeholder="Ratings" :disabled="readOnlyMode" v-model="formData.field_p1_rating10" name="field_p1_rating10" id="field_p1_rating10">
                                        <option value='' selected=""><span class="text-muted">Ratings...</span></option>
                                        <option v-for="number in 5" :value="number">{{ number }}</option>
                                    </select>
                                </div>
                            </div>
                            <div class="row bg-white">
                                <div class="col-lg-10 border-grey border py-1 px-2 odoo-cell-grey d-flex align-items-center">
                                    <strong>Total score - Consolidated total 50/10. Sample rating. 40/10 = 4 (Above expected performance</strong>
                                </div>
                                <div class="col-lg-2 odoo-cell-grey" style="padding: 0px">
                                    <div class="full_height_input small_text d-flex align-items-center justify-content-center">
                                        {{ totalScore }}
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </form>
            </div>    
        </div>
    `,
}