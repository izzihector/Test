MEmployeeAssessment = {
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
          if (newVal.value) this.writeDataToForm(newVal);
        },
        immediate: true,
        deep: true,
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
            this.formData['has_sup_assessments_feed'] = true
            this.formData['p3_q1_sup_comments'] = data.value['p3_q1_sup_comments']
            this.formData['p3_q2_sup_comments'] = data.value['p3_q2_sup_comments']
            this.formData['p3_q3_sup_comments'] = data.value['p3_q3_sup_comments']
            this.formData['p3_q4_sup_comments'] = data.value['p3_q4_sup_comments']
        },
        async submitForm() {
            this.disableButton = true
            this.buttonText = "Saving..."
            result = await this.submitFunction(this.formData)
            if (result) {
                this.changeReadOnlyMode(changeData=false)
                if (this.appraisalData.value.metaInfo.employee_assessment_state){
                    this.changeComponent('MCareerAspiration')
                }
            }
            this.disableButton = false
            this.buttonText = "Save and next"
        }

  },
  template: `
        <div>
        <h4 style="font-size: 20px;background: #ffffff;padding: 10px 0;margin-top: 20px;border-bottom: 4px solid #875a7b;text-transform: uppercase;">Technical and behavioral competencies Assessment</h4>
        <div class="text-center">
        <svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" data-name="Layer 1" width="200" height="200" viewBox="0 0 811.75984 620"><path d="M269.03284,759.032l-.03789.24566c-.04493-.23913-.08817-.4842-.12926-.72552-.0751-.39-.14026-.7804-.20168-1.17321a95.55112,95.55112,0,0,1,3.9079-45.76336q1.4428-4.30709,3.28655-8.45606a93.74713,93.74713,0,0,1,19.64776-28.70874,40.444,40.444,0,0,1,9.11275-6.99233c.49254-.26095.98777-.50827,1.494-.73628a16.67145,16.67145,0,0,1,9.998-1.44878,13.63552,13.63552,0,0,1,3.55957,1.195c.39479.192.77486.40275,1.14774.6276a19.75625,19.75625,0,0,1,8.64631,13.22952,30.86278,30.86278,0,0,1-.43488,12.03106q-.12025.56508-.25842,1.12548a62.70539,62.70539,0,0,1-2.48907,7.73053C316.31349,726.86214,294.89039,749.619,269.03284,759.032Z" transform="translate(-194.12008 -140)" fill="#f2f2f2"/><path d="M319.60412,666.55063q-11.66777,16.76675-22.04379,34.3838-10.36341,17.60241-19.37144,35.9573-5.03919,10.26928-9.63774,20.74671c-.33941.773.80562,1.44544,1.14941.66249q8.21254-18.70334,17.82456-36.7486,9.6061-18.02687,20.56148-35.2903,6.12971-9.65806,12.66693-19.04891c.48734-.7003-.66386-1.36023-1.14941-.66249Z" transform="translate(-194.12008 -140)" fill="#fff"/><path d="M327.92735,692.42374a36.42583,36.42583,0,0,1-23.9464,13.87842,34.62039,34.62039,0,0,1-7.99383.15838c-.8516-.08051-.85755,1.24678-.01326,1.32661a37.74921,37.74921,0,0,0,27.36864-8.64847,35.94791,35.94791,0,0,0,5.73426-6.05245c.51143-.68053-.64145-1.33842-1.14941-.66249Z" transform="translate(-194.12008 -140)" fill="#fff"/><path d="M278.00347,733.63185a30.495,30.495,0,0,1-3.36463-6.22033,32.17041,32.17041,0,0,1-2.06693-15.79595q1.4428-4.30709,3.28655-8.45606a.75827.75827,0,0,1,.06128.74918,29.11531,29.11531,0,0,0-1.85428,6.46168,30.74813,30.74813,0,0,0,5.08981,22.60357.53935.53935,0,0,1,.08813.51977A.72267.72267,0,0,1,278.00347,733.63185Z" transform="translate(-194.12008 -140)" fill="#fff"/><path d="M304.81723,666.61825a30.873,30.873,0,0,0,1.36,19.17961.66706.66706,0,0,0,.90485.24695.67955.67955,0,0,0,.24695-.90486,29.38117,29.38117,0,0,1-1.23217-18.17246.66361.66361,0,0,0-1.27965-.34924Z" transform="translate(-194.12008 -140)" fill="#fff"/><path d="M268.86976,726.99737l.08056.23515c-.15087-.19089-.303-.38783-.45149-.58245-.24765-.31046-.48672-.62594-.72358-.94526a95.55132,95.55132,0,0,1-17.79739-42.34159q-.723-4.4844-1.01758-9.015a93.74705,93.74705,0,0,1,4.06347-34.55018,40.4442,40.4442,0,0,1,4.82181-10.42521c.315-.45989.63863-.909.981-1.346a16.67146,16.67146,0,0,1,8.18086-5.92728,13.63548,13.63548,0,0,1,3.70734-.59523c.43877-.01341.87327-.00329,1.30792.02263a19.75622,19.75622,0,0,1,13.80225,7.69916,30.8628,30.8628,0,0,1,5.20357,10.85625q.156.55628.294,1.11673a62.70413,62.70413,0,0,1,1.38678,8.00208C295.79609,676.54608,287.39569,706.65021,268.86976,726.99737Z" transform="translate(-194.12008 -140)" fill="#f2f2f2"/><path d="M270.69414,621.608q-2.544,20.26793-3.54911,40.6888-1.00074,20.40206-.45166,40.84086.3078,11.43489,1.10248,22.84944c.0585.84217,1.38487.90579,1.32562.05274q-1.4154-20.37786-1.28578-40.823.13295-20.42616,1.81535-40.803.94185-11.4002,2.36872-22.75305c.10626-.84654-1.21975-.89619-1.32562-.05275Z" transform="translate(-194.12008 -140)" fill="#fff"/><path d="M290.08349,640.65387a36.42578,36.42578,0,0,1-14.75918,23.41381,34.6199,34.6199,0,0,1-7.00546,3.85357c-.79154.32429-.18026,1.50245.6045,1.181a37.74923,37.74923,0,0,0,20.21922-20.37208,35.948,35.948,0,0,0,2.26654-8.02351c.13678-.84022-1.18977-.88729-1.32562-.05274Z" transform="translate(-194.12008 -140)" fill="#fff"/><path d="M265.01488,700.33692a30.49551,30.49551,0,0,1-5.86906-3.94554,32.17063,32.17063,0,0,1-9.168-13.02816q-.723-4.4844-1.01758-9.015a.75824.75824,0,0,1,.40228.635,29.11512,29.11512,0,0,0,1.35951,6.58357,30.7482,30.7482,0,0,0,15.00719,17.65254.5393.5393,0,0,1,.31949.41935A.72267.72267,0,0,1,265.01488,700.33692Z" transform="translate(-194.12008 -140)" fill="#fff"/><path d="M257.63085,628.53667a30.873,30.873,0,0,0,10.11372,16.353.66707.66707,0,0,0,.916-.20163.67954.67954,0,0,0-.20164-.916,29.38112,29.38112,0,0,1-9.53266-15.52047.66361.66361,0,0,0-1.29544.28516Z" transform="translate(-194.12008 -140)" fill="#fff"/><path d="M269.44389,759.19523l.19452.15475c-.22993-.07959-.46417-.1636-.6941-.24761-.37587-.12821-.74721-.26528-1.11876-.40677a95.55124,95.55124,0,0,1-37.79944-26.09137q-3.02434-3.38909-5.71256-7.0479a93.7471,93.7471,0,0,1-15.18363-31.29991,40.44371,40.44371,0,0,1-1.55185-11.381c.0177-.55711.04857-1.1098.10168-1.66249a16.67157,16.67157,0,0,1,3.70086-9.40015,13.636,13.636,0,0,1,2.80318-2.49817c.36248-.2476.734-.47307,1.11423-.68533a19.75621,19.75621,0,0,1,15.776-.94618A30.86284,30.86284,0,0,1,241.3053,674.028q.431.38468.84911.78261a62.70373,62.70373,0,0,1,5.47811,5.99558C264.96041,702.1842,274.09533,732.07364,269.44389,759.19523Z" transform="translate(-194.12008 -140)" fill="#f2f2f2"/><path d="M214.22223,669.41313q8.772,18.44757,18.92306,36.1952,10.14459,17.72943,21.61482,34.65515,6.41775,9.4691,13.2348,18.65884c.50285.6781,1.6547.01736,1.14536-.66949Q256.9729,741.845,246.0711,724.54841q-10.88877-17.28237-20.44541-35.35767-5.34613-10.11288-10.25811-20.44709c-.36638-.77051-1.5104-.09821-1.14535.66948Z" transform="translate(-194.12008 -140)" fill="#fff"/><path d="M240.81684,675.01854a36.4258,36.4258,0,0,1,.17395,27.67689,34.61982,34.61982,0,0,1-3.82731,7.01984c-.49229.69954.65729,1.363,1.14536.66949a37.74921,37.74921,0,0,0,6.06476-28.05454,35.948,35.948,0,0,0-2.41141-7.98116c-.33727-.78162-1.48034-.10685-1.14535.66948Z" transform="translate(-194.12008 -140)" fill="#fff"/><path d="M251.83749,738.80763a30.495,30.495,0,0,1-7.07011-.1636,32.17048,32.17048,0,0,1-14.74127-6.0398q-3.02434-3.38909-5.71256-7.0479a.75827.75827,0,0,1,.68093.31836,29.11553,29.11553,0,0,0,4.69117,4.815,30.74817,30.74817,0,0,0,22.15184,6.79144.53938.53938,0,0,1,.495.18127A.72268.72268,0,0,1,251.83749,738.80763Z" transform="translate(-194.12008 -140)" fill="#fff"/><path d="M206.94684,682.28657a30.873,30.873,0,0,0,17.32878,8.33189c.3581.04766.65985-.339.66323-.66323a.67954.67954,0,0,0-.66323-.66323,29.38112,29.38112,0,0,1-16.39083-7.94337c-.61481-.59262-1.554.34414-.938.93794Z" transform="translate(-194.12008 -140)" fill="#fff"/><path d="M359.98141,584.24891a10.74268,10.74268,0,0,0,1.58187-16.3965l4.16719-93.01794-21.21552,2.3813,1.23255,90.98468a10.80091,10.80091,0,0,0,14.23391,16.04846Z" transform="translate(-194.12008 -140)" fill="#ffb8b8"/><polygon points="204.564 601.708 216.639 603.83 228.573 558.267 212.752 555.134 204.564 601.708" fill="#ffb8b8"/><path d="M395.12335,741.026h38.53073a0,0,0,0,1,0,0v14.88687a0,0,0,0,1,0,0H410.0102a14.88686,14.88686,0,0,1-14.88686-14.88686v0A0,0,0,0,1,395.12335,741.026Z" transform="translate(498.80399 1417.38394) rotate(-170.02922)" fill="#2f2e41"/><polygon points="171.422 607.752 183.682 607.751 189.514 560.463 171.42 560.464 171.422 607.752" fill="#ffb8b8"/><path d="M362.91494,744.24846h38.53073a0,0,0,0,1,0,0v14.88687a0,0,0,0,1,0,0H377.80179a14.88686,14.88686,0,0,1-14.88686-14.88686v0A0,0,0,0,1,362.91494,744.24846Z" transform="translate(570.27483 1363.36634) rotate(179.99738)" fill="#2f2e41"/><path d="M417.69451,734.8025a4.75008,4.75008,0,0,1-.57252-.03389l-14.43-1.18741a4.88077,4.88077,0,0,1-4.24251-5.65951l13.32468-74.681-9.00352-47.474a1.62706,1.62706,0,0,0-3.219.15995L388.29589,732.55435a4.92369,4.92369,0,0,1-5.2096,4.43715l-13.59479-.50632a4.88783,4.88783,0,0,1-4.53645-4.631l-.91385-151.76761,70.48116-8.80968,4.9236,76.04057-.01959.0805-16.99071,83.675A4.88582,4.88582,0,0,1,417.69451,734.8025Z" transform="translate(-194.12008 -140)" fill="#2f2e41"/><circle cx="193.15865" cy="249.99669" r="24.56103" fill="#ffb8b8"/><path d="M410.42125,591.17892a20.11,20.11,0,0,1-10.85692-3.10569c-11.89736-7.43585-25.41059-4.48057-32.40686-2.057a4.88009,4.88009,0,0,1-4.22053-.48089,4.81083,4.81083,0,0,1-2.2244-3.55163L347.99,468.35816c-2.132-19.03768,9.33586-36.93668,27.2677-42.55965h0q1.01052-.317,2.05519-.60112a39.56866,39.56866,0,0,1,32.972,5.72254,40.20349,40.20349,0,0,1,17.1668,29.35307l10.71048,114.3871a4.80738,4.80738,0,0,1-1.52715,4.0071C432.88054,582.14044,421.98336,591.17786,410.42125,591.17892Z" transform="translate(-194.12008 -140)" fill="#875a7b"/><path d="M371.68013,492.72437l-28.70337-3.156a5.71747,5.71747,0,0,1-4.90543-7.13382l7.30606-27.84637a15.87852,15.87852,0,0,1,31.55638,3.56326l1.08461,28.67531a5.71749,5.71749,0,0,1-6.33825,5.89758Z" transform="translate(-194.12008 -140)" fill="#875a7b"/><path d="M438.04732,580.26582a10.74264,10.74264,0,0,0-.40564-16.46763L430.56875,470.956l-20.78851,4.67965,12.20288,90.41406a10.80091,10.80091,0,0,0,16.0642,14.21613Z" transform="translate(-194.12008 -140)" fill="#ffb8b8"/><path d="M401.81017,486.888a5.7113,5.7113,0,0,1-1.81845-4.39983l1.08461-28.67532a15.87852,15.87852,0,0,1,31.55638-3.56326l7.30606,27.84637a5.71749,5.71749,0,0,1-4.90543,7.13383l-28.70337,3.156A5.711,5.711,0,0,1,401.81017,486.888Z" transform="translate(-194.12008 -140)" fill="#875a7b"/><path d="M385.81792,415.48307a5.683,5.683,0,0,1-1.29663-.15137l-.12475-.03027c-21.59449-3.30371-26.3667-15.81153-27.41431-21.03516-1.08423-5.4082.15039-10.62842,2.94019-12.65576-1.521-4.80273-1.27686-9.061.72729-12.66211,3.49536-6.28027,11.08106-8.40381,12.09839-8.66357,6.05811-4.46924,13.3064-1.48584,14.62524-.88086,11.71851-4.33545,16.19751-.72657,17.00757.0791,5.23828.94092,8.43115,2.96435,9.49121,6.01562,1.991,5.731-4.30542,12.85987-4.57446,13.16065l-.13965.15576-9.38013.44678a6.358,6.358,0,0,0-5.9812,7.31689h0a29.60406,29.60406,0,0,0,.96045,3.35547c1.602,5.00635,2.80225,9.2832,1.25415,10.90918a2.50968,2.50968,0,0,1-2.62524.45508c-1.46655-.3916-2.4624-.30957-2.9585.24463-.77026.85937-.53515,3.03466.66211,6.12549a5.73887,5.73887,0,0,1-1.0459,5.84716A5.56805,5.56805,0,0,1,385.81792,415.48307Z" transform="translate(-194.12008 -140)" fill="#2f2e41"/><path d="M675.87992,494h-121a17.01917,17.01917,0,0,1-17-17V295.16846a17.01916,17.01916,0,0,1,17-17h121a17.01916,17.01916,0,0,1,17,17V477A17.01917,17.01917,0,0,1,675.87992,494Zm-121-213.83154a15.017,15.017,0,0,0-15,15V477a15.017,15.017,0,0,0,15,15h121a15.017,15.017,0,0,0,15-15V295.16846a15.017,15.017,0,0,0-15-15Z" transform="translate(-194.12008 -140)" fill="#3f3d56"/><path d="M657.37988,365.58447h-84a8.50951,8.50951,0,0,1-8.5-8.5v-40a8.50951,8.50951,0,0,1,8.5-8.5h84a8.50981,8.50981,0,0,1,8.5,8.5v40A8.50981,8.50981,0,0,1,657.37988,365.58447Z" transform="translate(-194.12008 -140)" fill="#875a7b"/><path d="M651.38,403.08434h-72a8,8,0,1,1,0-16h72a8,8,0,0,1,0,16Z" transform="translate(-194.12008 -140)" fill="#ccc"/><path d="M651.38,433.08434h-72a8,8,0,1,1,0-16h72a8,8,0,0,1,0,16Z" transform="translate(-194.12008 -140)" fill="#ccc"/><path d="M651.38,463.08434h-72a8,8,0,1,1,0-16h72a8,8,0,0,1,0,16Z" transform="translate(-194.12008 -140)" fill="#ccc"/><path d="M970.87992,596h-121a17.01917,17.01917,0,0,1-17-17V397.16846a17.01916,17.01916,0,0,1,17-17h121a17.01916,17.01916,0,0,1,17,17V579A17.01917,17.01917,0,0,1,970.87992,596Zm-121-213.83154a15.017,15.017,0,0,0-15,15V579a15.017,15.017,0,0,0,15,15h121a15.017,15.017,0,0,0,15-15V397.16846a15.017,15.017,0,0,0-15-15Z" transform="translate(-194.12008 -140)" fill="#3f3d56"/><path d="M946.38,425.08434h-72a8,8,0,1,1,0-16h72a8,8,0,0,1,0,16Z" transform="translate(-194.12008 -140)" fill="#ccc"/><path d="M946.38,455.08434h-72a8,8,0,1,1,0-16h72a8,8,0,0,1,0,16Z" transform="translate(-194.12008 -140)" fill="#ccc"/><path d="M952.37988,531.584h-84a8.51013,8.51013,0,0,1-8.5-8.5v-40a8.51014,8.51014,0,0,1,8.5-8.5h84a8.51013,8.51013,0,0,1,8.5,8.5v40A8.51012,8.51012,0,0,1,952.37988,531.584Z" transform="translate(-194.12008 -140)" fill="#e6e6e6"/><path d="M946.38,567.08434h-72a8,8,0,1,1,0-16h72a8,8,0,0,1,0,16Z" transform="translate(-194.12008 -140)" fill="#ccc"/><path d="M896.87992,307h-121a17.01917,17.01917,0,0,1-17-17V177.16846a17.01916,17.01916,0,0,1,17-17h121a17.01916,17.01916,0,0,1,17,17V290A17.01917,17.01917,0,0,1,896.87992,307Zm-121-144.83154a15.017,15.017,0,0,0-15,15V290a15.017,15.017,0,0,0,15,15h121a15.017,15.017,0,0,0,15-15V177.16846a15.017,15.017,0,0,0-15-15Z" transform="translate(-194.12008 -140)" fill="#3f3d56"/><path d="M872.38,271.58434h-72a8,8,0,1,1,0-16h72a8,8,0,0,1,0,16Z" transform="translate(-194.12008 -140)" fill="#ccc"/><path d="M872.38,241.58434h-72a8,8,0,1,1,0-16h72a8,8,0,0,1,0,16Z" transform="translate(-194.12008 -140)" fill="#ccc"/><path d="M872.38,211.58434h-72a8,8,0,1,1,0-16h72a8,8,0,0,1,0,16Z" transform="translate(-194.12008 -140)" fill="#ccc"/><circle cx="488.75984" cy="143" r="23" fill="#875a7b"/><path d="M680.60009,291.774a2.38531,2.38531,0,0,1-1.43527-.47675l-.02567-.01928-5.40515-4.13837a2.40139,2.40139,0,1,1,2.921-3.81237l3.50105,2.68456,8.27354-10.7899a2.40128,2.40128,0,0,1,3.36684-.44444l-.05144.06984.05278-.06883a2.4041,2.4041,0,0,1,.44444,3.36687L682.5106,290.8368A2.40237,2.40237,0,0,1,680.60009,291.774Z" transform="translate(-194.12008 -140)" fill="#fff"/><circle cx="788.75984" cy="246" r="23" fill="#3f3d56"/><path d="M980.60009,394.774a2.38531,2.38531,0,0,1-1.43527-.47675l-.02567-.01928-5.40515-4.13837a2.40139,2.40139,0,1,1,2.921-3.81237l3.50105,2.68456,8.27354-10.7899a2.40128,2.40128,0,0,1,3.36684-.44444l-.05144.06984.05278-.06883a2.4041,2.4041,0,0,1,.44444,3.36687L982.5106,393.8368A2.40237,2.40237,0,0,1,980.60009,394.774Z" transform="translate(-194.12008 -140)" fill="#fff"/><circle cx="715.75984" cy="23" r="23" fill="#3f3d56"/><path d="M907.60009,171.774a2.38531,2.38531,0,0,1-1.43527-.47675l-.02567-.01928-5.40515-4.13837a2.40139,2.40139,0,1,1,2.921-3.81237l3.50105,2.68456,8.27354-10.7899a2.40128,2.40128,0,0,1,3.36684-.44444l-.05144.06984.05278-.06883a2.4041,2.4041,0,0,1,.44444,3.36687L909.5106,170.8368A2.40237,2.40237,0,0,1,907.60009,171.774Z" transform="translate(-194.12008 -140)" fill="#fff"/><path d="M576.12008,760h-381a1,1,0,0,1,0-2h381a1,1,0,1,1,0,2Z" transform="translate(-194.12008 -140)" fill="#3f3d56"/></svg>
      </div>
      <legend class="mb-3 page-hint"><p class="hint">
      This section will focus on how the employee has demonstrated and integrated their profesioanl/technical and behavioral competencies in their day to day work including integration of SCA policies and values</p></legend>   
            <div class="py-1">
                <form class="form-group" @submit.prevent="submitForm">
                    <div class="form_buttons" v-if="appraisalData.value.metaInfo.hasCurrentComponentAccess">
                        <button type="button" class="btn btn-secondary text-white" @click="changeReadOnlyMode" v-if="!disableButton">{{ editButtonText }}</button>
                        <button  class="btn btn-secondary text-white" :disabled="disableButton" v-if="!readOnlyMode">{{ buttonText }}</button>
                    </div>
                    <fieldset>
                    <div class="grand-parent">

                      <div class="objectives-parent">
                        <div class="objectives-child">
                          <span style="width:100%;">Question 1.</span>
                          <p class="objective-learning-body">
                          How has the employee demonstrated their technical skills and competencies in the day-to-day work during the review period in terms of the professional skills, knowledge, accuracy of work, timelines and meeting deadlines and analysis of information for value addition to their work? Use specific examples where necessary
                          </p>
                        </div>
                      </div>

                      <div class="objectives-parent">
                        <div class="objectives-child">
                          <span style="width:100%;">Employee Comment</span>
                          <p class="objective-body">
                          {{ appraisalData.value['p3_q1_emp_comments'] }}
                          </p>
                        </div>
                      </div>

                      <div class="objectives-parent">
                          <div class="objectives-child">
                            <span style="width:100%;">Supervisor Comment</span>
                            <textarea class="form-control disabled-textarea" rows="5" placeholder="Supervisor Comment..." :disabled="readOnlyMode" 
                            v-model="formData.p3_q1_sup_comments" name="p3_q1_sup_comments" id="p3_q1_sup_comments"></textarea>
                          </div>
                      </div>
                    </div>

                    <div class="grand-parent">
                     <div class="objectives-parent">
                      <div class="objectives-child">
                          <span style="width:100%;">Question 2.</span>
                          <p class="objective-learning-body">
                          How has the employee demonstrated their skills and competencies working with others through communication, coordination, and collaboration as a member of the team, supervisor, or line manager with the unit/department? Please cite examples and incidents where appropriate.
                          </p>
                        </div>
                      </div>

                      <div class="objectives-parent">
                        <div class="objectives-child">
                          <span style="width:100%;">Employee Comment</span>
                          <p class="objective-body">
                          {{ appraisalData.value['p3_q2_emp_comments'] }}
                          </p>
                        </div>
                      </div>

                      <div class="objectives-parent">
                          <div class="objectives-child">
                            <span style="width:100%;">Supervisor Comment</span>
                            <textarea class="form-control disabled-textarea" rows="5" placeholder="Supervisor Comment..." :disabled="readOnlyMode" 
                            v-model="formData.p3_q2_sup_comments" name="p3_q2_sup_comments" id="p3_q2_sup_comments"></textarea>
                          </div>
                      </div>

                    </div>

                    <div class="grand-parent">
                      <div class="objectives-parent">
                        <div class="objectives-child">
                            <span style="width:100%;">Question 3.</span>
                            <p class="objective-learning-body">
                            How has the employee proved their leadership ability to work independently, under pressure, leading through a crisis, adapting to changes  developing others through delegation and support?
                            </p>
                        </div>

                        </div>

                        <div class="objectives-parent">
                          <div class="objectives-child">
                            <span style="width:100%;">Employee Comment</span>
                            <p class="objective-body">
                            {{ appraisalData.value['p3_q3_emp_comments'] }}
                            </p>
                          </div>
                        </div>

                        <div class="objectives-parent">
                            <div class="objectives-child">
                              <span style="width:100%;">Supervisor Comment</span>
                              <textarea class="form-control disabled-textarea" rows="5" placeholder="Supervisor Comment..." :disabled="readOnlyMode" 
                          v-model="formData.p3_q3_sup_comments" name="p3_q3_sup_comments" id="p3_q3_sup_comments"></textarea>
                            </div>
                        </div>

                    </div>

                    <div class="grand-parent">
                      <div class="objectives-parent">
                        <div class="objectives-child">
                            <span style="width:100%;">Question 4.</span>
                            <p class="objective-learning-body">
                            How has the employee integrated the SCA policies and values <strong>(responsiveness, equality, impartiality, social justice and integrity)</strong> in the day-to-day work during the review period. Key pointers include gender, diversity and inclusion (GDI), enforcing and reinforcing policies, relationship building and support to colleagues, field teams, partners and key stakeholders etc.) Please cite specific examples that demonstrated application and integration of the values.
                            </p>
                        </div>

                        </div>

                        <div class="objectives-parent">
                          <div class="objectives-child">
                            <span style="width:100%;">Employee Comment</span>
                            <p class="objective-body">
                            {{ appraisalData.value['p3_q4_emp_comments'] }}
                            </p>
                          </div>
                        </div>

                        <div class="objectives-parent">
                            <div class="objectives-child">
                              <span style="width:100%;">Supervisor Comment</span>
                              <textarea class="form-control disabled-textarea" rows="5" placeholder="Supervisor Comment..." :disabled="readOnlyMode" 
                              v-model="formData.p3_q4_sup_comments" name="p3_q4_emp_comments" id="p3_q4_emp_comments"></textarea>
                            </div>
                        </div>

                    </div>

                    </fieldset>

                </form>
            </div>    
        </div>
    `,
};
